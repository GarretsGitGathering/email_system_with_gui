import PySimpleGUI as sg
import os.path
import sys

from receive import getEmails
from timezone import calculateTimestamp, calculateSeconds

# Save the original sys.stdout for later use
original_stdout = sys.stdout

### TOP ROW COLUMN ###
main_column = [
    ### GET TIME ###
    [
        sg.Text("Input Desired Past Date (MM/DD/YYYY):"),
        sg.In(size=(10, 2), enable_events=True, key="-DATE-"),
    ],
    [
        sg.Text("Input Time of Day (HH:MM)"),
        sg.In(size=(10, 2), enable_events=True, key="-TIME-"),
    ],

    ### GET CREDENTIALS ###
    [
        sg.Text("Credential"),
        sg.In(size=(25, 2), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
        )
    ],

    ### SEND EMAILS BUTTON ###
    [
       sg.Button('Get Emails', key="-SEND-")
    ]
]

### BOTTOM ROW COLUMN ###
email_column = [[sg.Text("Emails_received:")],
                [sg.Multiline(size=(60, 20), key='-OUTPUT-', autoscroll=True)]]

### layout ###
layout = [[  # top row
    sg.Column(main_column),
    sg.VSeperator(),
    sg.Column(email_column),
]]

window = sg.Window("Email Reciever", layout)

### VARIABLES ###
filename = ""
past_timestamp = 0
time_back = 0
check = False

while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "-DATE-":
        past_timestamp = calculateTimestamp(values["-DATE-"])

    if event == "-TIME":
        time_back = calculateSeconds(values["-TIME-"])

    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
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
            and f.lower().endswith((".json"))
        ]
        window["-FILE LIST-"].update(fnames)
        check = True

    # File List event triggered, update list with filenames in 'values'
    elif event == "-FILE LIST-" and check:  # A file was chosen from the listbox
        filename = os.path.join(
            values["-FOLDER-"], values["-FILE LIST-"][0]        # THIS IS WHAT WE WANT TO PASS TO getEmails
        )

    elif event == '-SEND-':
        # Redirect sys.stdout to the Output element
        sys.stdout = window['-OUTPUT-']

        # Perform some terminal-like print statements
        if filename != "" or past_timestamp == 0 or time_back == 0:
            print(getEmails(credentials_file=filename, past_time=(past_timestamp+time_back)))
        else:
            print("MAKE SURE ALL FIELDS ARE FILLED")

        # Reset sys.stdout to the original value
        sys.stdout = original_stdout

window.close()
