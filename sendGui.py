import PySimpleGUI as sg
import os
import sys
from send import schedule_and_send_emails
from timezone import calculateSeconds, calculateTimestamp

# Save the original sys.stdout for later use
original_stdout = sys.stdout

### TOP ROW COLUMN ###
main_column = [
    ### GET TIME ###
    [
        sg.Text("Desired Scheduled Date (MM/DD/YYYY):"),
        sg.In(size=(10, 2), enable_events=True, key="-DATE-"),
    ],
    [
        sg.Text("Scheduled Time of Day (HH:MM)"),
        sg.In(size=(10, 2), enable_events=True, key="-TIME-"),
    ],
    ### GET CSV ###
    [
        sg.Text("Email CSV Sheet"),
        sg.In(size=(25, 2), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse()
    ],
    [sg.Listbox(values=[], enable_events=True, size=(60, 10), key="-FILE_LIST-")]
]

### DOMAIN AND API KEY COLUMN ###
domain_and_email_column = [
    [sg.Text("Domain Name:")],
    [sg.In(size=(25, 2), enable_events=True, key="-DOMAIN_NAME-")],
    [sg.Text("API Key:")],
    [sg.In(size=(25, 2), enable_events=True, key="-API_KEY-")]]

### SUBJECT AND EMAIL ROW ###
subject_and_email_row = [
    [sg.Text("Insert Subject:")],
    [sg.In(size=(25, 2), enable_events=True, key="-SUBJECT-")],
    [sg.Text("Insert Email HTML here:")],
    [sg.Text("'-FULL_NAME-' = client Full Name")],
    [sg.Text("'-CLIENT_ADDRESS-' = client address")],
    [sg.Text("'-CLIENT_CITY-' = client city'")],
    [sg.Text("'-CLIENT_STATE-' = client state")],
    [sg.Multiline(size=(60, 20), enable_events=True, key='-EMAIL_HTML-', autoscroll=True)],
    [sg.Button('Send Emails', key="-SEND-")]]

### CHECKSTATUS COLUMN ###
checkstatus_column = [[sg.Text("Scheduled Emails:")],
                [sg.Multiline(size=(50, 40), key='-OUTPUT-', autoscroll=True)]]

### layout ###
layout = [[  
            sg.Column(main_column),
            sg.VSeperator(),
            sg.Column(domain_and_email_column),
        ],
        [
            sg.Column(subject_and_email_row),
            sg.VSeparator(),
            sg.Column(checkstatus_column)
        ]
        ]


### VARIABLES ###
day_timestamp = 0
hour_timestamp = 0
csv_file_name = ""
email_subject = ""
email_html = ""
DOMAIN_NAME = ""
API_KEY = ""
check = False

# Create the window
window = sg.Window("Email Sender", layout)

# Create an event loop
while True:
    event, values = window.read()

    if event == "-DATE-":
        day_timestamp = calculateTimestamp(values["-DATE-"])

    elif event == "-TIME-":
        hour_timestamp = calculateSeconds(values["-TIME-"])

    # Folder name was filled in, make a list of files in the folder
    elif event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".csv"))
        ]
        window["-FILE_LIST-"].update(fnames)
        check = True

    # FILE_LIST event triggered, update list with filenames in 'values'
    elif event == "-FILE_LIST-" and check:  # A file was chosen from the listbox
        csv_file_name =  values["-FILE_LIST-"][0]

    elif event == "-SUBJECT-":
        email_subject = values["-SUBJECT-"]

    elif event == "-EMAIL_HTML-":
        email_html = values["-EMAIL_HTML-"]

    elif event == "-DOMAIN_NAME-":
        DOMAIN_NAME = values["-DOMAIN_NAME-"]

    elif event == "-API_KEY-":
        API_KEY = values["-API_KEY-"]
    
    # presses the OK button
    elif event == "-SEND-":
        # Redirect sys.stdout to the Output element
        sys.stdout = window['-OUTPUT-']

        if(DOMAIN_NAME!="" and API_KEY!="" and csv_file_name!="" and email_subject!="" and email_html!="" and day_timestamp!=0 and hour_timestamp!=0):
            ### schedule emails and print logs ###
            print(schedule_and_send_emails(DOMAIN_NAME, API_KEY, csv_file_name, email_subject, email_html, day_timestamp+hour_timestamp))  
        else:
            if(DOMAIN_NAME==""):
                print("Domain Name is empty.")
            if(API_KEY==""):
                print("API key is empty.")
            if(csv_file_name==""):
                print("csv file name is empty")
            if(email_subject==""):
                print("subject is empty.")
            if(email_html==""):
                print("email html is empty")
            if(day_timestamp==0 or hour_timestamp==0):
                print("time info is empty or incorrect")

        # Reset sys.stdout to the original value
        sys.stdout = original_stdout 
    
    elif event == sg.WIN_CLOSED:
        break

window.close()
