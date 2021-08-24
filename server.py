# Read env vars from .env file
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.api import plaid_api
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from datetime import datetime
from datetime import timedelta
import plaid
import datetime
import json
import time

app = Flask(__name__)

# Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
PLAID_CLIENT_ID = '611eef354388c800107c7528'
PLAID_SECRET = '9bd80fa6147e53e3032624be315f5d'

configuration = plaid.Configuration(
  host=plaid.Environment.Development,
  api_key={
    'clientId': PLAID_CLIENT_ID,
    'secret': PLAID_SECRET,
  }
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

access_token = None
item_id = None

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def format_error(e):
    response = json.loads(e.body)
    return {'error': {'status_code': e.status, 'display_message':
                      response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}}


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

@app.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():
    global access_token
    public_token = request.form['public_token']
    req2 = ItemPublicTokenExchangeRequest(
      public_token=public_token
    )
    response = client.item_public_token_exchange(req2)
    access_token = response['access_token']
    print(access_token)
    item_id = response['item_id']

    return jsonify(response.to_dict())


# Retrieve an Item's accounts
@app.route('/accounts', methods=['GET'])
def get_accounts():
  try:
      request = AccountsGetRequest(
          access_token=access_token
      )
      accounts_response = client.accounts_get(request)
  except plaid.ApiException as e:
      response = json.loads(e.body)
      return jsonify({'error': {'status_code': e.status, 'display_message':
                      response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}})
  return jsonify(accounts_response.to_dict())

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    # Pull transactions for the last 30 days
    start_date = (datetime.datetime.now() - timedelta(days=730))
    end_date = datetime.datetime.now()

    options = TransactionsGetRequestOptions(count=500)
    frozen = 10

    #Time out after 30 seconds
    while True:  
        try:
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date.date(),
                end_date=end_date.date(),
                options=options
            )
            response = client.transactions_get(request)
            return jsonify(response.to_dict())

        except plaid.ApiException as e:
            time.sleep(3)
            frozen -= 1
            if frozen < 1:
                error_response = format_error(e)
                return jsonify(error_response)
    





@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


@app.route("/", methods=['GET'])
def login():
  return render_template("link.html")


if __name__ == "__main__":
    app.run(port=8000,debug=True)