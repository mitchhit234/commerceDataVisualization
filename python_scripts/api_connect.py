#Template code for setting up connection with GMAIL API
#and handling storing credentials
import pickle
import os
import traceback
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from pathlib import Path

ABSOLUTE = str(Path(__file__).parents[1])


def Create_Service(client_secret_file, api_name, api_version, *scopes):
    #print(client_secret_file, api_name, api_version, scopes, sep='-')
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    #print(SCOPES)
    
    cred = None
    pickle_file = f'{ABSOLUTE}/resources/token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
    
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        #refresh function not working, we will just ask for user authentication
        #again when token expires
        if cred and cred.expired and cred.refresh_token:
            try:
                cred.refresh(Request())
            except:
                print("Refresh error, creating new token file")
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                cred = flow.run_local_server()
                with open(pickle_file, 'wb') as token:
                    pickle.dump(cred, token)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

            with open(pickle_file, 'wb') as token:
                pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        traceback.print_exc()
        return None
