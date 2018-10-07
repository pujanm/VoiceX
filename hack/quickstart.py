from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import maya


#762680543836-nqnk0qn3ubjl8v1dbe7d18f80gn2teeo.apps.googleusercontent.com
#AIzaSyCPSEEL4h5uPdX5IAokLHUdUAxM45jGKJE

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.events'

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    s = maya.when("9th October")
    date = s.datetime().strftime("%Y-%m-%d")

    event = {
    	'description': 'A chance to hear more about Google\'s developer products.',
    	'start': {
    		'date': date,
    		'timeZone': 'Asia/Kolkata',
    	},
    	'end': {
    		'date': date,
    		'timeZone': 'Asia/Kolkata',
    	},
    	'recurrence': [
    		'RRULE:FREQ=DAILY;COUNT=2'
    	],
    	'reminders': {
    		'useDefault': False,
    		'overrides': [
    			{'method': 'email', 'minutes': 24 * 60},
    			{'method': 'popup', 'minutes': 10},
    		],
    	},
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

        

if __name__ == '__main__':
    main()
