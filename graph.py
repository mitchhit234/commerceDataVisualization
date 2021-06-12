import matplotlib.pyplot as plt 
import db_create as db


DB_NAME = "transaction.db"
TABLE_NAME = "TRANSACTIONS"
CURRENT_VALUE = 3188.71


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


if __name__ == "__main__":
  conn = db.create_database(DB_NAME)
  cursor = conn.cursor()

  #Fetch all current data
  statement = "SELECT * FROM " + TABLE_NAME
  cursor.execute(statement)
  data = cursor.fetchall()


  start = fetch_starting(data[::-1], CURRENT_VALUE)

  # x = []
  # y = []
  # for i in data:
  #   if not i[3]:
  #     y.append(i[4])
  #   else:
  #     y.append(i[3])
  #   x.append(i[1])



  # plt.plot(x,y)


  # plt.xlabel('x axis')
  # plt.ylabel('y axis')
  # plt.title('graph')

  # plt.show()