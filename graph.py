import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from pandas.core.frame import DataFrame
import db_create as db
from datetime import date

import plotly.offline as py
import plotly.graph_objects as go
import pandas as pd






#Default filenames, change as needed
DB_NAME = "transaction.db"
TABLE_NAME = "TRANSACTIONS"
#Will change this to an input later
CURRENT_VALUE = 3133.91



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

#Initalize the current column
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

  for _, row in D.iterrows():
    if row['date'] == current:
      count += 1
    #New date found, list of old dates are given
    #evenly spaced times 
    else:
      update_date_list(ret,count,current)
      current = row['date']
      count = 1

  #Catch any transactions remaining after our loop 
  update_date_list(ret,count,current)
  return ret
  

#Inserts dates in order of occurence into our
#eventual new date column
def update_date_list(L,count,current):
  denom = count + 1
  for i in range(1,denom):
    hr_extension = int((i/denom)*24)
    L.append(current + " " + str(hr_extension))
  return L


#Truncate information not needed from the date
#up till the date part inputed inclusive
# y = year, m = month, d = day
def truncate_date(D,typ):
  temp = []
  for _, row in D.iterrows():
    if typ == 'y':
      temp.append(row['date'][:4])
    elif typ == 'm':
      temp.append(row['date'][:7])
    else:
      temp.append(row['date'][:10])

  D['date'] = temp
  return D


#Configure X axis and rangeslider
def set_fig_x_axis(figure,C,L,S,mode,slide):
  config = []
  for c, l, s in zip(C,L,S):
    temp = mode
    if l == "YTD":
      temp = "todate"
    temp = dict(count=c,label=l,step=s,stepmode=temp)
    config.append(temp)

  config.append(dict(step="all"))



  figure.update_layout(
    xaxis=dict(
      rangeselector=dict(
        buttons=config,font=dict(size=11)),
      rangeslider=dict(
        visible=slide
      ),
      type="date"
    )
  )

  figure.update_xaxes(rangeslider_thickness = 0.1)

  return figure



#Plotting transaction number against 
#current value, given a list of transactions
#and the starting balance before those transactions
def balance_plot(D):
  #Make credit and debit price charts format nicer
  # D.replace(to_replace=[0], value=np.nan, inplace=True)

  #Figure containing lines for debit, credit, and net account balance
  # fig = go.Figure()
  # for col in D.columns[3:]:
  #   if col != 'net':
  #     m = 'markers'
  #     if col == 'current':
  #       m = 'lines'
  #     fig.add_trace(go.Scatter(x=D['date'], y=D[col], mode=m, name=col))

  #Figure containing net account balance
  fig = go.Figure()
  fig.add_trace(go.Scatter(x=D['date'], y=D['current'], mode='lines', 
    line=dict(width=3,color="#03DA00"), name='Current Balance', customdata=D['description']))
  
  #Configure variables for graph X axis
  counts = [1, 7, 1, 6, 1, 1]
  labels = ["Day", "Week", "Month", "6 Months", "YTD", "Year"]
  steps = ["day", "day", "month", "month", "year", "year"]
  stepmode = "backward"

  fig = set_fig_x_axis(fig,counts,labels,steps,stepmode,True)

  #Set div settings for margin, backround, and height
  #Can't find a way to have the height fit to parent div
  fig.update_layout(margin=dict(l=20,r=20,t=20,b=20),
    height=700,
    title=dict(text='ACCOUNT BALANCE',x=0.5,y=1,xanchor='center',yanchor='top'),
    yaxis_title=dict(text='Dollars',standoff=10),
    font=dict(family="Lucida Bright, monospace",size=13)
  )

  div_output = py.plot(fig,include_plotlyjs=False, output_type='div',config=dict(responsive=True))

  return div_output
  



#Pass type credit, debit, or net for accompying graph
def specalized_plot(D,typ):

  #Obtain a new dataframe to only show year and month in date variable
  M_DF = truncate_date(D.copy(),'m')
  cur_date = M_DF['date'][0]
  cur_debit = cur_credit = 0
  raw = []
  for _, row in M_DF.iterrows():
    if row['date'] == cur_date:
      cur_debit += row['debit']
      cur_credit += row['credit']
    else:
      raw.append(dict(date=cur_date,debit=round(cur_debit,2),credit=round(cur_credit,2)))
      cur_date, cur_debit, cur_credit = row['date'], row['debit'], row['credit']

  #Final date will not be covered in the above loop
  raw.append(dict(date=cur_date,debit=round(cur_debit,2),credit=round(cur_credit,2)))

  #Conver our list of dictionaries to a dataframe, add
  #a net balance column
  monthDF = pd.DataFrame(raw)
  monthDF['net'] = monthDF['credit'] - monthDF['debit']
  

  #Bar Graph color handling
  green = '#32CD32'
  red = '#FF0000'

  if typ == 'credit':
    cl = green
  elif typ == 'debit':
    cl = red

  if typ == 'net': 
    colors = []
    for _, row in monthDF.iterrows():
      if row['net'] < 0:
        colors.append(red)
      else:
        colors.append(green)
    monthDF['color'] = colors
  else:
    monthDF['color'] = cl



  fig=go.Figure()
  fig.add_trace(go.Bar(x=monthDF['date'], y=monthDF[typ],
    marker=dict(color=monthDF['color'])))

  counts = [6, 1, 5]
  labels = ["6 Months", "Year", "5 Years"]
  steps = ["month", "year", "year"]
  stepmode = "backward"

  fig = set_fig_x_axis(fig,counts,labels,steps,stepmode,False)
    

  fig.update_layout(margin=dict(l=20,r=20,t=20,b=20),
    height=700,
    title=dict(text=typ.upper() + ' HISTORY',x=0.5,y=1,xanchor='center',yanchor='top'),
    yaxis_title=dict(text='Dollars',standoff=10),
    font=dict(family="Lucida Bright, monospace",size=13),
    hovermode='x'
  )

  div_output = py.plot(fig,include_plotlyjs=False, output_type='div',
    config=dict(responsive=True))

  return div_output


#Read from our DB and get our dataframe set up
def initalize():
  conn = db.create_database(DB_NAME)
  cursor = conn.cursor()

  #Fetch all current data
  statement = "SELECT * FROM " + TABLE_NAME + " ORDER BY num"
  cursor.execute(statement)
  data = cursor.fetchall()

  #Create a net value column
  df = pd.read_sql_query(statement,conn)
  df = df.fillna(0)
  df['net'] = df['credit'] - df['debit']

  #our first transaction stored in the database
  start = fetch_starting(df.iloc[::-1], CURRENT_VALUE)
  df['current'] = fetch_current(df,start)
  
  #Prevent overlaps on our graph
  df['date'] = adjust_dates(df)

  return df






