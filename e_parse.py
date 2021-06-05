#Only good for debits right now, need to get 
#a direct deposit email to configure credits
import database_creation
import os
import datetime
import eml_parser
from bs4 import BeautifulSoup

#datetime = ['header']['date']

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


database_name = "app.db"
table_name = "TRANSACTIONS"
dir_name = "alerts"
#In this case, create database just connects to an already 
#exisiting database, if trying to create a new database,
#add the additional create_table function to make tables for it
conn = database_creation.create_database(database_name)
cursor = conn.cursor()
current_num = get_next_num(cursor)


for filename in os.listdir(dir_name):
  if filename.endswith(".eml"):
    
    #Get the body contents from our email file
    ep = eml_parser.EmlParser()
    parsed_eml = ep.decode_email(dir_name + "/" + filename)
    a = ep.get_raw_body_text(ep.msg)[0]
    html = a[1]

    #Use html processing to get the text from our body contents
    soup = BeautifulSoup(html, 'html.parser')
    r = soup.find_all('font')

    #Ordered as date, description, debit, credit
    #Come back and tweak once credit email format is examined
    values = [reorder_date(r[3].text), str(current_num), f'"{r[4].text}"', clean_money(r[5].text), 'NULL']
    statement = database_creation.generate_insert_sql(table_name, values)
    cursor.execute(statement)

    #Increment num value to keep track of order
    #for same date transactions
    current_num += 1


conn.close()

