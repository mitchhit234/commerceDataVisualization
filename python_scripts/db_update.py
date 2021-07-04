#Meant to run before every application launch
#Will update the database based off of commerce alerts

#Current known transactions commerce doesn't give alerts to (and would 
#have to be entered manually or through the export method)
#Transfer from another commerece account
#Direct deposits (gives alert to action and desc, but not price)

from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import base64

import db_create as db
from api_connect import Create_Service


#Default file names and other variables
#Change only if needed
ABSOLUTE = str(Path(__file__).parents[1])
RESOURCES = ABSOLUTE + "/resources/"
CLIENT_SECRET_FILE = RESOURCES + "api_id.json"
API_NAME = "gmail"
API_VERSION = "v1"
SCOPES = ["https://mail.google.com/"]
DB_NAME = RESOURCES + "transaction.db"
TABLE_NAME = "TRANSACTIONS"
ALERT_ADDRESS = "CommerceBankAlerts@commercebank.com"


#Returns True if d1 is greater than  or
#equal to d2, otherwise returns False
#Date format is YYYY-MM-DD
def compare_dates(d1,d2):
  d1, d2 = d1.replace('-',''), d2.replace('-','')
  return int(d1) >= int(d2)

#Orders the date from the email to the 
#correct format for SQLite DATE variable
def reorder_date(st):
  st = st.split('-')
  ret = ''
  for i in range(2,len(st)+2):
    index = i % len(st)
    ret += st[index] + '-'
  return f'"{ret[:-1]}"'

#Cleans the money value from the email to
#display as an INT in SQLite
def clean_money(st):
  st = st.replace('$','')
  st = st.replace(' ','')
  st = st.replace(',','')
  return st

#Must match Column name as it appears in DB table
def get_max_col(cur,col_name,tbl_name):
  statement = "SELECT MAX(" + col_name + ") FROM " + tbl_name
  cur.execute(statement)
  return cur.fetchone()[0]

#Select all the transactions from the last key (usually date)
def get_last_transactions(cur,key,tbl_name):
  statement = "SELECT * FROM " + tbl_name + " WHERE " + key + " = "
  statement += "(SELECT MAX(" + key + ") FROM " + tbl_name + ")"
  cur.execute(statement)
  return cur.fetchall()

#Prevent insertion of data already inserted in the DB
#Issues could arise later here, not the best logic
def prevent_repeats(inst,repeats):
  for i in range(len(repeats)):
    if comp(repeats[i][3],inst[3]) or comp(repeats[i][4],inst[4]):
      return False
  return True

#Compare values that could be either a number as a string
#in different percision formats or strings containing 'None'
def comp(x,y):
  if str(x) == 'None' and str(y) == 'None':
    return True
  elif float(x) == float(y):
    return True
  return False



#Will help fetch the correct part of the email
#for various email formats
def find_correct_mimeType(P):
  for i in P:
    if i['mimeType'] == 'text/html':
      return i['body']['data']


#Depth indicates how many entries max
#will be returned from our GMail query
def update(DEPTH):
  #Getting connected to the API for this user
  #based on their credentials file
  service = Create_Service(CLIENT_SECRET_FILE,API_NAME, API_VERSION,SCOPES)

  #Getting connected to the Data
  #And retreving needed information for insertions
  conn = db.create_database(DB_NAME)
  cursor = conn.cursor()
  current_num = get_max_col(cursor,"num",TABLE_NAME) + 1
  last_date = get_max_col(cursor,"date",TABLE_NAME)
  last_entries = get_last_transactions(cursor,"date",TABLE_NAME)

  #Query via the GMail API for message IDs
  L = service.users().messages().list(userId='me', maxResults=DEPTH, q='from:' + ALERT_ADDRESS).execute()

  #Parse through each email
  valid_values = []
  for i in L['messages']:
    email_id = i['id']
    mesg_obj = service.users().messages().get(userId='me', id=email_id).execute()
    payload = mesg_obj['payload']['parts']
    encoded_body = find_correct_mimeType(payload)
    html_body = base64.urlsafe_b64decode(encoded_body)
    
    #Use html processing to get the text from our body contents
    soup = BeautifulSoup(html_body, 'html.parser')
    r = soup.find_all('font')

    #8 total font tags represent the format for a debit alert
    if len(r) == 8:
      #Ordered as date, description, debit, credit
      date = reorder_date(r[3].text)
      #Checking if this date is later than our last insertion
      #in the database, i.e. is this a new transaction
      if compare_dates(date.strip('"'),last_date):
        #Prepare the parsed info for an Insert Statement
        values = [reorder_date(r[3].text), str(0), r[4].text, clean_money(r[5].text), 'None']
        if prevent_repeats(values,last_entries):
          values = [reorder_date(r[3].text), str(0), 
                    f'"{r[4].text}"', clean_money(r[5].text), 'NULL']         
          valid_values.append(values)

    #5 total font tags represent the format for a direct deposit alert
    elif len(r) == 5:
      headers = mesg_obj['payload']['headers']
      date = ''
      for i in headers:
        if i['name'] == 'Date':
          date = i['value'][5:16]
          break
      
      #formatting raw data for datatable insertion
      date_obj = datetime.strptime(date,'%d %b %Y')
      #gmail seems to consistently report days as one day earlier
      date_obj = date_obj + timedelta(days=1)
      clean_date = date_obj.strftime('%Y-%m-%d')
      desc = r[2].text.split(':')[1]

      if compare_dates(clean_date,last_date):

        #We need user input since commerce alerts will not give us the dollar amount
        print('What is the value of this direct deposit transaction?\nDate: {} \nDescription: {}'.format(clean_date,desc))
        money = input()

        values = [f'"{clean_date}"', str(0), f'"{desc}"', 'None', clean_money(money)]

        if prevent_repeats(values,last_entries):
          values[3] = 'NULL'
          valid_values.append(values)
            
      

  #GMail query returns emails from newest to oldest
  #We want to insert those in the reverse order
  valid_values.reverse()

  for i in valid_values:
    #Update current num place holder
    i[1] = str(current_num)
    current_num += 1

    #Insert approved transaction into table
    statement = db.generate_insert_sql(TABLE_NAME,i)
    print(statement)
    try:
      cursor.execute(statement)
    except db.Error as e:
      db.traceback.print_exc()

  conn.commit()
  conn.close()
