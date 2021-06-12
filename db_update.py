from api_connect import Create_Service
from bs4 import BeautifulSoup
import base64
import db_create as db


#More default file names and other variables
#Change only if needed
CLIENT_SECRET_FILE = "credentials.json"
API_NAME = "gmail"
API_VERSION = "v1"
SCOPES = ["https://mail.google.com/"]
DB_NAME = "transaction.db"
TABLE_NAME = "TRANSACTIONS"
#Depth indicates how many entries max
#will be returned from our GMail query
DEPTH = 100
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
  return st

#Must match Column name as it appears in DB table
def get_max_col(cur,col_name,tbl_name):
  statement = "SELECT MAX(" + col_name + ") FROM " + tbl_name
  cur.execute(statement)
  return cur.fetchone()[0]

#Will help fetch the correct part of the email
#for various email formats
def find_correct_mimeType(P):
  for i in P:
    if i['mimeType'] == 'text/html':
      return i['body']['data']



if __name__ == "__main__":
  #Getting connected to the API for this user
  #based on their credentials file
  service = Create_Service(CLIENT_SECRET_FILE,API_NAME, API_VERSION,SCOPES)

  #Getting connected to the Data
  #And retreving needed information for insertions
  conn = db.create_database(DB_NAME)
  cursor = conn.cursor()
  current_num = get_max_col(cursor,"num",TABLE_NAME) + 1
  last_date = get_max_col(cursor,"date",TABLE_NAME)

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
        values = [reorder_date(r[3].text), str(0), 
                  f'"{r[4].text}"', clean_money(r[5].text), 'NULL']   
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
