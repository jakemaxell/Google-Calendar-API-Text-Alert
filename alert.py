import smtplib
import os.path
from datetime import datetime, timedelta, timezone
import json
from email.message import EmailMessage

from google.auth.transport.requests import Request as AuthRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def getCalendarData():
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    CALENDAR_IDS = ["abeyy315@gmail.com", "jmaxwell@tocafootball.com"]

    creds = None

    if(os.path.exists('googleCreds.json')):
        with open('googleCreds.json', 'r') as file:
            credsData = json.load(file)

        creds = Credentials.from_authorized_user_info(credsData, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(AuthRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("googleCreds.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("googleCreds.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        calendar_timezone = timezone(timedelta(hours=-5))  # Eastern Standard Time is UTC-5

        now = datetime.now(calendar_timezone)

        start_of_day = datetime(now.year, now.month, now.day, tzinfo=calendar_timezone)
        end_of_day = start_of_day + timedelta(days=1)

        start_of_day_str = start_of_day.isoformat()
        end_of_day_str = end_of_day.isoformat()
        
        allEvents = []
        for calendar_Id in CALENDAR_IDS:
            eventsResult = (
                service.events()
                .list(
                    calendarId=calendar_Id,
                    timeMin=start_of_day_str,
                    timeMax=end_of_day_str,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                ).execute()
            )

            events = eventsResult.get("items", [])
            allEvents.extend(events)

        return allEvents
    except HttpError as error:
        print(error)

    return None

def stringifyCalendar():
    returnData = "Good Morning Jacob. Here are your events of today. Have a good day! :)\n"

    counter = 1
    myList = getCalendarData()
    for event in myList:
        try:
            dateString = event['start']['dateTime']
            dateObject = datetime.fromisoformat(dateString)
            dateFormatted = dateObject.strftime("%Y-%m-%d %H:%M:%S")
        except:
            dateString = event['start']['date']
            dateObject = datetime.fromisoformat(dateString)
            dateFormatted = dateObject.strftime("%Y-%m-%d %H:%M:%S")

        returnData = returnData + "\n" + str(counter) + ": " + event['summary'] + " starts at " + dateFormatted + "\n"
        counter = counter + 1

    return returnData

def textAlert():
    user = "my-email@gmail.com"
    password = "fake-password"

    message = EmailMessage()
    message.set_content(stringifyCalendar())
    message['to'] = "{insert cell number}@txt.att.net"

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user, password)
    server.send_message(message)

    server.quit()

textAlert()
