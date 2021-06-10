from re import M

from oauthlib.oauth2.rfc6749.clients import base
from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import database_creation
import os
import datetime
import eml_parser
from bs4 import BeautifulSoup


def reorder_date(st):
  st = st.split('-')
  ret = ''
  for i in range(2,len(st)+2):
    index = i % len(st)
    ret += st[index] + '-'
  return f'"{ret[:-1]}"'

def clean_money(st):
  st = st.replace('$','')
  st = st.replace(' ','')
  return st

def get_next_num(cur):
  statement = "SELECT MAX(num) FROM TRANSACTIONS"
  cur.execute(statement)
  return cur.fetchone()[0] + 1

def find_correct_mimeType(P):
  for i in P:
    if i['mimeType'] == 'text/html':
      return i['body']['data']


CLIENT_SECRET_FILE = "credentials.json"
API_NAME = "gmail"
API_VERSION = "v1"
SCOPES = ["https://mail.google.com/"]

service = Create_Service(CLIENT_SECRET_FILE,API_NAME, API_VERSION,SCOPES)


database_name = "app.db"
table_name = "TRANSACTIONS"
dir_name = "alerts"

# msg = "If you are seeing this you are poggers"
# mimeMessage = MIMEMultipart()
# mimeMessage['to'] = "mdmfvz@umsystem.edu"
# mimeMessage['subject'] = "POGGERS"
# mimeMessage.attach(MIMEText(msg, 'plain'))
# raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
#message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()\


alert_address = "CommerceBankAlerts@commercebank.com"
L = service.users().messages().list(userId='me', maxResults=100, q='from:commercebankalerts@commercebank.com').execute()

current_num = 0

for i in L['messages']:
  email_id = i['id']
  mesg_obj = service.users().messages().get(userId='me', id=email_id).execute()
  payload = mesg_obj['payload']['parts']
  encoded_body = find_correct_mimeType(payload)
  html_body = base64.urlsafe_b64decode(encoded_body)
  

  #Use html processing to get the text from our body contents
  soup = BeautifulSoup(html_body, 'html.parser')
  r = soup.find_all('font')

  if len(r) == 8:

    #Ordered as date, description, debit, credit
    #Come back and tweak once credit email format is examined
    values = [reorder_date(r[3].text), str(current_num), f'"{r[4].text}"', clean_money(r[5].text), 'NULL']
    statement = database_creation.generate_insert_sql(table_name, values)

    print(statement)
    
    current_num += 1

  #headers = mesg_obj['payload']['headers']
  # commerce_alert = False
  # for j in range(len(headers)):
  #   if headers[j]['name'] == "From":
  #     if alert_address in headers[j]['value']:
  #       commerce_alert = True
  #       print("In")
  #     break

