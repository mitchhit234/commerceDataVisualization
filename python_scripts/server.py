from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.api import plaid_api
from flask import Flask, redirect, url_for
from flask import render_template
from flask import request
from flask import jsonify
from datetime import datetime
from datetime import timedelta
from os import path
from pathlib import Path
from dotenv import load_dotenv
from threading import Timer
import pandas as pd
import plaid
import datetime
import json
import time
import webbrowser
import os

#Default filenames, change as needed
ABSOLUTE = str(Path(__file__).parents[1])
RESOURCES = ABSOLUTE + '/resources/'
ACCESS_TOKEN_FILE = RESOURCES + 'access_token.txt'
TRANSACTIONS_FILE = RESOURCES + 'transactions.json'

#Load our .env variables
load_dotenv()
app = Flask(__name__)

#Grab PLAID variables from .env file
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')

#Configured for development environment
configuration = plaid.Configuration(
  host=plaid.Environment.Development,
  api_key={
    'clientId': PLAID_CLIENT_ID,
    'secret': PLAID_SECRET,
  }
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

#Check if theres an access token to read in
if path.exists(ACCESS_TOKEN_FILE):
    with open(ACCESS_TOKEN_FILE, 'r') as inp:
        access_token = inp.read().replace('\n','')
else:
    access_token = None
item_id = None

#Shutdown after transaction data is recieved in order to 
#transition into the data analysis application
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#Debug help
def format_error(e):
    response = json.loads(e.body)
    return {'error': {'status_code': e.status, 'display_message':
                      response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}}

#Catch different date formats output by plaid
#including YYYY-MM-DD and when datetime format
def normalize_date(date_string):
    if "GMT" in date_string:
        date_string = date_string[5:16]
        date_string = date_string.replace(" ","-")
        date_string = datetime.datetime.strptime(date_string,'%d-%b-%Y').strftime('%Y-%m-%d')    
    return date_string

#Get most recent transaction date from plaid json file
def get_most_recent_date(filename):
    with open(TRANSACTIONS_FILE, 'r') as inp:
        data = json.load(inp)
    temp = pd.json_normalize(data, record_path=['transactions'])
    date_string = normalize_date(temp.iloc[0]['date'])
    date = date_string.split('-')

    return datetime.date(int(date[0]),int(date[1]),int(date[2]))

#Open specified url, used in function for threading purposes
def open_browser():
    webbrowser.open_new_tab('https://localhost:8000')

@app.route("/create_link_token", methods=['POST'])
def create_link_token():
    # Get the client_user_id by searching for the current user
    client_user_id = 'mitchhit234'
    # Create a link_token for the given user
    req = LinkTokenCreateRequest(
            products=[Products("auth")],
            client_name="Plaid Test App",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=client_user_id
            )
        )
    response = client.link_token_create(req)
    # Send the data to the client
    return jsonify(response.to_dict())

#After link token is created, exchange it for an access
#token, which will be stored and used later for Plaid API requests
@app.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():
    global access_token
    public_token = request.form['public_token']
    req2 = ItemPublicTokenExchangeRequest(
      public_token=public_token
    )
    response = client.item_public_token_exchange(req2)
    access_token = response['access_token']
    with open(ACCESS_TOKEN_FILE, 'w') as output:
        output.write(access_token)

    #redirect to get transaction data
    #return redirect(url_for('get_transactions'))

#Request used for gaining transaction data needed to populate
#the data analytics application
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    # Pull transactions for the last 2 years (or last 500 transactions)
    # if none avaliable, else pull only new transactions
    append = False
    if path.exists(TRANSACTIONS_FILE):
        start_date = get_most_recent_date(TRANSACTIONS_FILE)
        append = True
    else:
        start_date = (datetime.datetime.now() - timedelta(days=730))
        start_date = start_date.date()

    end_date = datetime.datetime.now().date()

    #Max transactions allowed in a single request
    options = TransactionsGetRequestOptions(count=500)
    
    #Time out variable in case of error
    frozen = 10

    #Time out after 30 seconds
    while True:  
        try:
            #Send the request for the transaction data
            #usually takes some time, which is the reason
            #behind having a for loop
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date,
                options=options
            )
            response = client.transactions_get(request)

            #Allow for multipule transaction requests if there are more 
            #transactions that can fit in a single response (500)
            while len(response['transactions']) < response['total_transactions']:
                request = TransactionsGetRequest(
                    access_token=access_token,
                    start_date=start_date,
                    end_date=end_date,
                    options=TransactionsGetRequestOptions(count=500,offset=len(response['transactions']))
                )
                resp = client.transactions_get(request)
                response['transactions'].extend(resp['transactions'])

            data = jsonify(response.to_dict())
            
            #If transaction file already exists, we try and append to that data
            if append:
                with open(TRANSACTIONS_FILE, 'r') as inp:
                    existing_data = json.load(inp)
                
                to_add, i = [], 0

                #Data is always fetched in date order, so once we hit a transaction we have
                #we know that we have all the transactions after
                while i < len(data.json['transactions']) and data.json['transactions'][i] != existing_data['transactions'][0]:
                    to_add.append(data.json['transactions'][i])
                    i += 1

                #Prepend these new transactions to the beggining of our transaction data
                existing_data['transactions'] = to_add + existing_data['transactions']
                data.json['transactions'] = existing_data['transactions'] 

            #Write transaction data to file         
            with open(TRANSACTIONS_FILE, 'w') as output:
                json.dump(data.json,output, indent=4)
                return redirect(url_for('shutdown'))
        
        #Wait 3 seconds to try and request transaction data again post failure
        except plaid.ApiException as e:
            time.sleep(3)
            frozen -= 1
            #After 30 seconds, return error message
            if frozen < 1:
                error_response = format_error(e)
                return jsonify(error_response)
    


@app.route('/shutdown', methods=['GET'])
def shutdown():
    #At this point, shutdown and bash script handles
    #switching over to the application
    shutdown_server()
    return 'Transaction data received'


@app.route("/", methods=['GET'])
def login():
    #Fetch access token if stored
    if path.exists(ACCESS_TOKEN_FILE):
        return redirect(url_for('get_transactions'))
    #Prompt user to login to recieve an access token
    return render_template("link.html")
        

if __name__ == "__main__":
    #One second delay webbrowser open to give app time to launch
    Timer(1, open_browser).start()
    app.run(host='0.0.0.0',ssl_context='adhoc', port=8000)
