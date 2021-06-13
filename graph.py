import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import db_create as db

import plotly.offline as py
import pandas as pd




#Default filenames, change as needed
DB_NAME = "transaction.db"
TABLE_NAME = "TRANSACTIONS"
#Will change this to an input later
CURRENT_VALUE = 3188.71


#Template for returning a plot object
def generate_plot(X,Y,x_label,y_label,title):
  plt.plot(X,Y)
  plt.xlabel(x_label)
  plt.ylabel(y_label)
  plt.title(title)
  return plt


#Given our current value, it gives our starting value
#before the earliest transaction recorded
def fetch_starting(D,current):
  for _ , row in D.iterrows():
    current -= row['net']
  #Round in case of floating point arithmetic getting wonky
  return round(current,2)


def fetch_current(D,current):
  ret = []
  for _, row in D.iterrows():
    current += row['net']
    ret.append(current)
  return ret
  
#Since date information from Commerce does not contain time
#I use this function to prevent transactions from stacking on top 
#of each other in our graphs by seperating them with hour variables
#Though not accurate to the hours IRL, they still contain correct order
def adjust_dates(D):
  ret = []
  current, count = "", 0
  for j, row in D.iterrows():
    if row['date'] == current:
      count += 1
    if row['date'] != current or j == len(D):
      denom = count + 1
      for i in range(1,denom):
        hr_extension = int((i/denom)*24)
        ret.append(current + " " + str(hr_extension))

      current = row['date']
      count = 1
    
      if j == len(D)-1:
        denom = count + 1
        for i in range(1,denom):
          hr_extension = int((i/denom)*24)
          ret.append(current + " " + str(hr_extension))



  return ret




#Plotting transaction number against 
#current value, given a list of transactions
#and the starting balance before those transactions
def plot_by_date(D):
  py.plot([{
    'x': D['date'],
    'y': D[col],
    'name': col
  } for col in D.columns[3:] if col != 'net'])






if __name__ == "__main__":
  conn = db.create_database(DB_NAME)
  cursor = conn.cursor()

  #Fetch all current data
  statement = "SELECT * FROM " + TABLE_NAME
  cursor.execute(statement)
  data = cursor.fetchall()

  df = pd.read_sql_query(statement,conn)
  df = df.fillna(0)
  df['net'] = df['credit'] - df['debit']

  #Starting value, i.e. the account balance before 
  #our first transaction stored in the database
  start = fetch_starting(df.iloc[::-1], CURRENT_VALUE)
  df['current'] = fetch_current(df,start)
  
  df['date'] = adjust_dates(df)

  plot_by_date(df)


