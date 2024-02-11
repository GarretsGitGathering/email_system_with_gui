import pandas as pd
import requests
import json

from timezone import get_timezone, get_rfc2822_time, breakdown_timestamp


### HELPER FUNCTION TO ITERATE THROUGH CSV FILE ###
def schedule_and_send_emails(DOMAIN_NAME, API_KEY, csv_file_name, email_subject, email_html, timestamp):

  ### CLEANSES DATA ###
  #data.dropna(inplace = True)

  ### READ DATA FROM CSV FILE ###
  data = pd.read_csv(csv_file_name)

  ### GET TIME INFO FROM TIMESTAMP ###
  year, month, day, hour, minute = breakdown_timestamp(timestamp)

  ### ITERATE THROUGH TIMESTAMP ###
  for index, recipient in data.iterrows():
    ### SCHEDULE EMAIL ###
    __schedule_email(DOMAIN_NAME, API_KEY, email_subject, email_html, recipient, year, month, day, hour, minute)

    ### MAKE LOGS ###
    logs = __check_status(DOMAIN_NAME, API_KEY, recipient, year, month, day, hour, minute)
    items = logs.json()['items']

    with open('logs.json', 'w', encoding='utf-8') as f:
      json.dump(items, f, ensure_ascii=False, indent=4)

    return logs
    

### METHOD TO CREATE EMAIL ###
def __schedule_email(DOMAIN_NAME, API_KEY, email_subject, email_html, recipient, year, month, day, hour, minute):
  
  ### GET LOCAL TIME ###
  timezone = get_timezone(recipient['City'], recipient['State'], recipient['Zip Code'], recipient['Country'])
  local_rfc2822_time = get_rfc2822_time(year, month, day, hour, minute, timezone)

  ### DEFAULT EMAIL HERE! ###
  # if(email_html==""):
  #   email_html = """
  #   <html>
  #     <body>
  #       <h1>Tom's Super Cool Business</h1>
  #       <p>To -FULL_NAME-</p>
  #       <br></br>
  #       <p>We heard about your experience at -COMPANY_NAME-. We are looking for a -TITLE- to join our team.
  #         We know you are located at -ADDRESS-, -CITY-, -STATE-</p>
  #       <br></br>
  #       <p>Thank you</p>
  #     </body>
  #   </html>
  #   """

  email_html = email_html.replace("-FULL_NAME-", recipient['Full Name'])
  email_html = email_html.replace("-COMPANY_NAME-", recipient['Company Name'])
  email_html = email_html.replace("-TITLE-", recipient['Title'])
  email_html = email_html.replace("-CLIENT_ADDRESS-", recipient['Address'])
  email_html = email_html.replace("-CLIENT_CITY-", recipient['City'])
  email_html = email_html.replace("-CLIENT_STATE-", recipient['State'])

   ### SEND POST REQUEST TO API ###
  requests.post(
   "https://api.mailgun.net/v3/" + DOMAIN_NAME + "/messages",
    auth=("api", API_KEY),
    data={
        "from": "Excited User <postmaster@" + DOMAIN_NAME + ">",
        "to": recipient['Email'],
        "subject": email_subject,
        "html": email_html,
        "o:deliverytime": local_rfc2822_time,
        'o:tracking-opens': True
    })
  
  print("email was scheduled to: " + recipient['Email'])


### CHECK STATUS OF EMAILS ###
def __check_status(DOMAIN_NAME, API_KEY, recipient, year, month, day, hour, minute):
  
  ### GET LOCAL TIME ###
  timezone = get_timezone(recipient['City'], recipient['State'], recipient['Zip Code'], recipient['Country'])
  local_rfc2822_time = get_rfc2822_time(year, month, day, hour, minute, timezone)

  print(local_rfc2822_time)
  email = recipient['Email']

  return requests.get(
      f"https://api.mailgun.net/v3/{DOMAIN_NAME}/events",
      auth=("api", API_KEY),
      params={"begin": local_rfc2822_time,
              "ascending": "yes",
              "limit": 25,
              "pretty": "yes",
              "recipient": email
              })