#Functions for reading in data, creating/manipulating dataframes,
#and creating interactive tables and graphs
import json
import numpy as np
import pandas as pd
from datetime import date
import plotly.graph_objects as go
from pathlib import Path
import datetime
import db_create as db


#Default filenames, change as needed
ABSOLUTE = str(Path(__file__).parents[1])
DB_NAME = ABSOLUTE + "/resources/transaction.db"
TABLE_NAME = "TRANSACTIONS"
META_TABLE = "META"

#Keep float numbers in currency format
pd.options.display.float_format = "${:.2f}".format


#Given our current balance value, it gives our starting value
#before the earliest transaction recorded
def generate_starting(D,current):
  for _ , row in D.iterrows():
    current -= row['net']
  #Round in case of floating point arithmetic getting wonky
  return round(current,2)



#If the starting value has already been calculated, we fetch that,
#otherwise we need to calculate it for balance plot rendering
def check_for_start(D,conn):
  statement = "SELECT balance FROM " + META_TABLE
  start = pd.read_sql_query(statement,conn)
  if start.empty:
    print('Enter your current (avaliable) account balance')
    current = input()
    cursor = conn.cursor()
    start = generate_starting(D.iloc[::-1],float(current))
    insert_meta_table(D['date'][0],start,cursor)
    conn.commit()
    conn.close()
  else:
    start = start['balance'][0]
  return start



#Insert our starting value for later retrevial into our META table
def insert_meta_table(date,value,cur):
  statement = 'INSERT INTO ' + META_TABLE + ' VALUES(' + f'"{date}", ' + str(value) + ')'
  cur.execute(statement)




#Initalize the current column
def fetch_balance_col(D,current):
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
  

#Convert float columns to 2 decimal string to 
#ensure they uphold the currency format
def format_dict_for_table(D):
  D['DATE'] = worded_date(D)

  float_col_name = ''
  for i in D.columns:
    if D[i].dtypes == 'float':
      float_col_name = i

  if len(float_col_name) > 0:
    D[float_col_name] = D[float_col_name].apply(lambda x: "{:.2f}".format(x))

  return D.to_dict('records')


#When dataframe is transfered to a dict,
#we lose our float formatting, so we have
#to reinitalize it for each float
def prepare_dict(D):
  dont_convert = ['DATE', 'NUM', 'DESCRIPTION']
  ret = D.to_dict('records')
  for i in range(len(ret)):
    for key in ret[i]:
      if key.upper() not in dont_convert:
        ret[i][key] = ret[i][key].format(ret[i][key], '.2f')
  return ret
      
#Grabs our base columns, date and description, plus
#one other column corresponding to its page and href
def grab_base_and_col(D,col_name):
  if len(col_name) < 2:
    col_name = 'BALANCE'
  base = ['DATE', 'DESCRIPTION', col_name.upper()]
  to_drop = []
  #Drop unwanted columns
  for i in D.columns:
    if i.upper() not in base:
      to_drop.append(i)
  D = D.drop(columns=to_drop)

  #Drop rows in which our specified
  #col values is 0
  if col_name != 'BALANCE':
    D = D.replace(0, np.nan)
    D = D.dropna(how='any',axis=0)
    D = D.replace(np.nan,0)

  return D

#Replace date column with worded version for easier
#table reading
def worded_date(D):
  temp = []
  for _,d in D.iterrows():
    row = d['DATE']
    temp.append(date(year=int(row[:4]), month=int(row[5:7]), day=int(row[8:10])).strftime('%b %d %Y'))
  return temp

#Convert possible datetime format to YYYY-MM-DD format
def normalize_dates(D):
  temp = []
  for _, row in D.iterrows():
    temp.append(normalize_date(row['date']))
  return temp



#Catch different date formats output by plaid
#including YYYY-MM-DD and when datetime format
def normalize_date(date_string):
  if "GMT" in date_string:
    date_string = date_string[5:16]
    date_string = date_string.replace(" ","-")
    date_string = datetime.datetime.strptime(date_string,'%d-%b-%Y').strftime('%Y-%m-%d')    
  return date_string




#Inserts dates in order of occurence into our
#eventual new date column
def update_date_list(L,count,current):
  denom = count + 1
  for i in range(1,denom):
    hr_extension = int((i/denom)*24)
    L.append(current + " " + str(hr_extension))
  return L

#Delete all data from a dataframe that does not fall
#within the given month
def month_only(D,month):
  to_remove = []



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


#Remove redundant information for simple presentation
#Normal description will still be avaliable to user
#via click actions
def summarize_desc(D):
  redundant_sub = ['CREDIT', 'DEBIT', 'CARD', 'PURCHASE', 'TRACE', 'RECURRING', 'PAYMENT', 'NO:']
  redundant_full = ['NO', 'ACH', '*', '-']

  temp = []
  for _, row in D.iterrows():
    raw = row['description'].split(' ')
    new = ' '
    for i in raw:
      i = i.upper()
      if i not in redundant_full:
        if not any(j in i for j in redundant_sub):
          if not any(x.isdigit() for x in i):
            new += i + ' '
    #removing prefix spaces that show up sometime for sorting reasons
    # while new[0] == ' ':
    #   new = new[1:]
    temp.append(new)

  return temp
  


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
        buttons=config,font=dict(size=14)),
      rangeslider=dict(
        visible=slide
      ),
      type="date"
    )
  )

  figure.update_xaxes(rangeslider_thickness = 0.1)

  return figure



#Plotting transaction number against 
#current balance value, given a list of transactions
#and the starting balance before those transactions
def balance_plot(D):
  fig = go.FigureWidget(go.Scatter(x=D['date'], y=D['balance'], mode='lines+markers', customdata=D['description'],hovertemplate='Balance: $%{y:.2f}'+'<br>Date: %{x} <extra></extra>'))

  #Configure variables for graph X axis
  counts = [1, 6, 1, 5]
  labels = ["1M", "6M", "1Y", "5Y"]
  steps = ["month", "month", "year", "year"]
  stepmode = "backward"

  fig = set_fig_x_axis(fig,counts,labels,steps,stepmode,False)

  #Set div settings for margin, backround, and height
  #Can't find a way to have the height fit to parent div
  fig.update_layout(margin=dict(l=20,r=20,t=20,b=20),
    #height=700,
    title=dict(text='ACCOUNT BALANCE \n',x=0.5,y=1,xanchor='center',yanchor='top'),
    font=dict(family="Helvetica, Lucida Bright",size=14)
  )

  #fig.update_layout(yaxis_tickformat = '$')
  fig.update_layout(title_text='ACCOUNT BALANCE', title_y=0.98)


  return fig




#Pass type credit, debit, or net for accompying graph
def specalized_plot(D,typ):
  # '/' or '' page is the home page, which shoud be the balance plot
  if len(typ) < 2:
    return balance_plot(D)

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
  else:
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


  #Figure creation, similar to balance plot but in bar chart format
  fig=go.Figure()
  fig.add_trace(go.Bar(x=monthDF['date'], y=monthDF[typ],
    marker=dict(color=monthDF['color']), hovertemplate='$%{y:.2f}<extra></extra>'))

  #Setting up the range selector buttons
  counts = [1, 6, 1, 5]
  labels = ["1M", "6M", "1Y", "5Y"]
  steps = ["month", "month", "year", "year"]
  stepmode = "backward"

  fig = set_fig_x_axis(fig,counts,labels,steps,stepmode,False)
    

  fig.update_layout(margin=dict(l=20,r=20,t=20,b=20),
    height=700,
    title=dict(text=typ.upper() + ' HISTORY',x=0.5,y=1,xanchor='center',yanchor='top'),
    font=dict(family="Helvetica, Lucida Bright",size=13)
  )

  fig.update_layout(yaxis_tickformat = '$')
  fig.update_layout(title_text=typ.upper() + ' HISTORY', title_y=0.98)

  return fig



def table_df(df,cols_to_discard):
  #Drop all columns we dont want to show
  df = df.drop(columns=cols_to_discard)

  #Condense description information
  if 'description' not in cols_to_discard:
    df['description'] = summarize_desc(df)

  #Present transactions from newset to oldes
  df = df.iloc[::-1]

  #Capitilize column names for better apperance
  df.columns = df.columns.str.upper()

  return df


#Read from our DB and get our dataframe set up
def initalize():
  conn = db.create_database(DB_NAME)

  #Fetch all current data
  statement = "SELECT * FROM " + TABLE_NAME + " ORDER BY num"

  #Create a net value column
  df = pd.read_sql_query(statement,conn)
  df = df.fillna(0)
  df['net'] = df['credit'] - df['debit']

  #Helps generate our balance plot
  start = check_for_start(df,conn)
  df['balance'] = fetch_balance_col(df,start)
  
  return df


#Read from our JSON data from Plaid instead of DB method
def json_initalize():
  with open('resources/transactions.json', 'r') as inp:
    data = json.load(inp)

  current_balance = data['accounts'][0]['balances']['available']

  temp_df = pd.json_normalize(data, record_path=['transactions'])
  cols = ['date','amount','name']
  df = temp_df[cols]
  df = df.iloc[::-1]

  df['date'] = normalize_dates(df)

  debit, credit, num = [], [], []
  for i, row in df.iterrows():
    if row['amount'] > 0:
      debit.append(row['amount'])
      credit.append(0)
    else:
      debit.append(0)
      credit.append(abs(row['amount']))
    num.append(i+1)
    
    
  df['amount'] = -df['amount']
  df['debit'], df['credit'], df['num'] = debit, credit, num

  df = df.rename({'amount': 'net', 'name': 'description'}, axis=1)

  start = generate_starting(df,current_balance)
  df['balance'] = fetch_balance_col(df,start)

  df = df[['date', 'num', 'description', 'debit', 'credit', 'net', 'balance']]

  return df



