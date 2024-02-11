import base64
import email
import os.path
import pickle
import time
from datetime import datetime

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

### METHOD TO GET EMAIL STATUS FROM GMAIL API ###
def getEmails(credentials_file, past_time):
    ### CREATE SCOPE TO ACCESS GMAIL API ###
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None
    body = ''
    body_list = []

    ### FIND PREVIOUS TIMESTAMP ###
    if os.path.exists("timestamp.txt"):
        f = open("timestamp.txt", "r")
        previous_timestamp = f.read()
        f.close()
    else:
        one_hour = 360000  # seconds
        previous_timestamp = time.time() - one_hour

    ### CREATE NEW TIMESTAMP ###
    timestamp = str(round(time.time()))
    f = open("timestamp.txt", "w")
    f.write(timestamp)
    f.close()

    ### CHECK IF token.json EXISTS FOR USER ###
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        ### READ TOKEN AND STORE IN OUR 'creds' VARIABLE ###
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    ### IF 'creds' DOESN'T EXIST, CREATE THEM ###
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the access token in token.pickle file for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    ### CONNECT TO GMAIL API ###
    service = build('gmail', 'v1', credentials=creds)

    #q=f"in: after:{previous_timestamp}",
    result = service.users().messages().list(userId='me', q=f"in: after:{past_time}", labelIds=['INBOX']).execute()
    
    # We can also pass maxResults to get any number of emails. Like this:
    # result = service.users().messages().list(maxResults=200, userId='me').execute()
    messages = result.get('messages')

    #iterate thriugh all the messages
    info = []
    if messages != None:
        for i, msg in enumerate(messages):

            # get message id
            txt = service.users().messages().get(userId='me', id=msg['id'], format="full").execute()

            try:
                #Get value of 'payload' from a dictionary 'txt
                payload = txt['payload']
                headers = payload['headers']

                # look for Subject and Sender Email in the headers
                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                    if d['name'] == 'From':
                        sender = d['value']

                # the returned body is encrypted in base64, so we will decrypt it. 
                parts = payload.get('parts')[0]
                data = parts['body']['data']
                data = data.replace("-", "+").replace("_", "/")

                # Now, the data obtained is in lxml. So, we will parse
                # it with BeautifulSoup library
                msg = base64.urlsafe_b64decode(data.encode('UTF8'))
                body = str(email.message_from_bytes(msg))
                body_list = body.split("\n")
                body_list = list(filter(None, body_list))

                #print(body)

                # append data to info list
                info.append((sender, subject, body_list))
            
            except Exception as e:
                print(e)
                continue

    return info