import json
import time
import data as dat
import cals


def listonline(service, calID, firstyear, lastyear):

    eventsList = []
    for numyear in range(firstyear, lastyear):
        year = str(numyear)
        for month in ('01', '02', '03', '04', '05', '06', '07', '08', '09',
                      '10', '11', '12'):
            thisMin = year+'-'+month+'-01T00:00:00Z'
            if month == '12':
                nextyear = str(int(year)+1)
                thisMax = nextyear+'-01-01T00:00:00Z'
            else:
                nextmonth = str(int(month)+1).zfill(2)
                thisMax = year+'-'+nextmonth+'-01T00:00:00Z'
            eventsResult = service.events().list(
                calendarId=calID, timeMin=thisMin, timeMax=thisMax,
                singleEvents=True, orderBy='startTime').execute()
            events = eventsResult.get('items', [])

            if not events:
                pass
            else:
                for event in events:
                    eventsList.append(event)
    return eventsList

def online2DictArray(service,calID,firstyear,lastyear):
  resultArray = []
  eventslist = listonline(service,calID,firstyear,lastyear)
# TODO: for each one, transform to JSON, read from there, show only needed fields
# http://stackoverflow.com/questions/13940272/python-json-loads-returns-items-prefixing-with-u
# eventslist[0] is a dict
  for event in eventslist:
    row = {}
    j_event = json.loads(json.dumps(event, ensure_ascii=False))
    #Good test for "description key error"
    #print(j_event)
    event_id = j_event["id"]
    summary = j_event["summary"]
    description = j_event["description"]
    start_datetime = j_event["start"]["dateTime"]
    end_datetime = j_event["end"]["dateTime"]
    row['event_id'] = event_id
    row['start_datetime'] = start_datetime
    row['end_datetime'] = end_datetime
    row['description'] = description
    row['summary'] = summary
    resultArray.append(row)

  return resultArray
## TODO: deprecate the old format, use the new one

def uploadCSV(service, csv_file, cal_name, zone, firstyear, lastyear):
  cal_id = cals.getIDCal(service, cal_name)
  entryDictArray = dat.CSV2DictArray(csv_file)
  for year in range(firstyear, lastyear):
    time.sleep(5)
    for entry in entryDictArray:
      if (str(year) == dat.CSVdatetime2gcal(entry['Start Date'], entry['Start Time'], zone).split('-')[0]):
        event = {
              'summary': entry['Subject'],
              'description': entry['Description'],
              'start': {
                       'dateTime': dat.CSVdatetime2gcal(entry['Start Date'], entry['Start Time'], zone),
                       },
              'end': {
                     'dateTime': dat.CSVdatetime2gcal(entry['End Date'], entry['End Time'], zone),
                     },
              'reminders': {
                           'useDefault': False,
                           'overrides': [
                                        {'method': 'popup', 'minutes': 10},
                                        ],
                           },
              }
        addEvent(service, dat.DictEntry2Gcal(event), cal_id)

def addEvent(service, event, cal_id):
  new_event = service.events().insert(calendarId=cal_id, body=event).execute()
  print ('Event created: ' + str(new_event))

def updateEvent(service, cal_id, event, event_id ):
  updated_event = service.events().update(calendarId=cal_id, eventId=event_id, body=event).execute()
  print ('Event updated: ' + str(updated_event))

def deleteEvent(service, event, cal_id, event_id):
  service.events().delete(calendarId=cal_id, eventId=event_id).execute()
