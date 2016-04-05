from datetime import datetime
import json

def listonline(service,calID):
    
    eventsList = []
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' for UTC time
    for numyear in range(2013, 2017):
        year=str(numyear)
        for month in ('01','02','03','04','05','06','07','08','09','10','11','12'): 
            thisMin=year+'-'+month+'-01T00:00:00Z'
            if month == '12':
                nextyear=str(int(year)+1)
                thisMax=nextyear+'-01-01T00:00:00Z'
            else:
                nextmonth=str(int(month)+1).zfill(2)
                thisMax=year+'-'+nextmonth+'-01T00:00:00Z'
            eventsResult = service.events().list(
                calendarId=calID, timeMin=thisMin, timeMax=year+'-'+nextmonth+'-01T00:00:00Z',
                singleEvents=True, orderBy='startTime').execute()
            events = eventsResult.get('items', [])

            if not events:
                pass
            else:
                for event in events:
                    eventsList.append(event)
    return eventsList

def listonlineCSV(service,calID):
  eventslist = listonline(service,calID)
# TODO: for each one, transform to JSON, read from there, show only needed fields  
# http://stackoverflow.com/questions/13940272/python-json-loads-returns-items-prefixing-with-u
# eventslist[0] is a dict
  print("event_id,subject,description,start_datetime,end_datetime,")
  for event in eventslist:
    j_event = json.loads(json.dumps(event, ensure_ascii=False))
    event_id = j_event["id"]
    subject = j_event["summary"]
    description = j_event["description"]
    start_datetime = j_event["start"]["dateTime"]
    end_datetime = j_event["end"]["dateTime"]
    print(event_id + "," + subject + "," + description + "," + start_datetime + "," + end_datetime + ",")

