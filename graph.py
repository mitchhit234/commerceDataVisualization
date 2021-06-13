import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import db_create as db


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
  for i in D:
    current -= net_value(i)
  #Round in case of floating point arithmetic getting wonky
  return round(current,2)


#Will return the credit value as positive
#or debit value as negative
def net_value(row):
  if row[3]:
    return -row[3]
  return row[4]


#Plotting transaction number against 
#current value, given a list of transactions
#and the starting balance before those transactions
def plot_by_transaction_num(D,current):
  x = [0]
  y = [current]
  for i in D:
    current += net_value(i)
    y.append(current)
    x.append(i[1])
  
  generate_plot(x,y,'Transaction Number',
    'Current Balance','Account Transactions')

  plt.show()






if __name__ == "__main__":
  conn = db.create_database(DB_NAME)
  cursor = conn.cursor()

  #Fetch all current data
  statement = "SELECT * FROM " + TABLE_NAME
  cursor.execute(statement)
  data = cursor.fetchall()

  #Starting value, i.e. the account balance before 
  #our first transaction stored in the database
  start = fetch_starting(data[::-1], CURRENT_VALUE)
  
  plot_by_transaction_num(data,start)


