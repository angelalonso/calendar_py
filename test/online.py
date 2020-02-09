import json
import time
import data as dat
import pill_calendar as pc

def newCal(service, cal_name):
  calendar = {'summary': cal_name}
  created_calendar = service.calendars().insert(body=calendar).execute()

def delCal(service, cal_name):
  calID = getIDCal(service, cal_name)
  service.calendars().delete(calendarId=calID).execute()
            

def getIDCal(service, cal_name):
  resultList = []
  page_token = None
  while True:
    cal_list = service.calendarList().list(pageToken=page_token).execute()
    for calendar_list_entry in cal_list['items']:
      if calendar_list_entry['summary'] == cal_name:
        resultList.append(calendar_list_entry['id'])
    page_token = cal_list.get('nextPageToken')
    if not page_token:
      break
  return resultList[0]


def conflict(event_offline, event_online):
  errors = []
  tests = ['event_id','start_datetime','end_datetime','description','summary']
  for test in tests:
    if (event_offline[test] != event_online[test]):
      errors.append(test)
  print("Attention! change on entry " + event_online['event_id'])
  for error in errors:
    print('- ' + error + ' old: ' + event_online[error] + ', new: ' + event_offline[error])
  print('Do you want to overwrite? ') 
  answer = 'wrong'
  while (answer != 'n' and answer != 'no' and
         answer != '' and answer != 'y' and answer != 'yes'):
    answer = raw_input("(y/n, default y) > ").lower()
  if (answer == 'y' or answer == 'yes' or answer == ''):
    return event_offline
  else:
    return event_online
    

def updateOnline(file_in):
  csv_events = dat.CSV2DictArray(file_in)
 #TODO: the following can be substituted for the online service list
  #online_events = csvs.readintoArray('online.csv')
  online_events = pc.loadCalendarFile('online.csv')
#TODO: add id-les, compare, update clear ones, show conflicts, ask for decision, automate decision
# same id, different calendar, different content -> default choose offline but show and  offer to revert
# different id, different calendar, same content <- update, choose offline, show message
  for csv_event in csv_events:
    if (csv_event['event_id'] == ""):
      print("##new one: " + str(csv_event))
    else:
      for onl_event in online_events:
      # Changed something on an existing ID?
        if (csv_event['event_id'] == onl_event['event_id']):
          if (csv_event['start_datetime'] != onl_event['start_datetime']
           or csv_event['end_datetime'] != onl_event['end_datetime']  
           or csv_event['description'] != onl_event['description']
           or csv_event['summary'] != onl_event['summary']):
            print('##conflict, chose: ' + str(conflict(csv_event,onl_event)))
# same id, same calendar different content
# different id, same calendar, same content -< clean up automatically(choose one), show message
# cleanup_cal(csv_event)
# cleanup_cal(onl_event)
  return ""

def updatefromCSV(service, csv_file, cal_name, zone, firstyear, lastyear):
  cal_id = getIDCal(service, cal_name)
  # lists
  csv_events = dat.CSV2DictArray(csv_file)
  online_events = online2DictArray(service, getIDCal(service, cal_name), firstyear, lastyear)
  for csv_event in csv_events:
    if (csv_event['event_id'] == ""):
      print("##new one: " + str(csv_event))
      addEvent(service, dat.DictEntry2Gcal(csv_event), cal_id)
    else:
      for onl_event in online_events:
      # Changed something on an existing ID?
        if (csv_event['event_id'] == onl_event['event_id']):
          if (csv_event['start_datetime'] != onl_event['start_datetime']
           or csv_event['end_datetime'] != onl_event['end_datetime']  
           or csv_event['description'] != onl_event['description']
           or csv_event['summary'] != onl_event['summary']):
            chosen_event = conflict(csv_event,onl_event)
            updateEvent(service, cal_id, dat.DictEntry2Gcal(chosen_event), chosen_event['event_id'] )
     
''' OLD EVENTS '''


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
  cal_id = online.getIDCal(service, cal_name)
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
