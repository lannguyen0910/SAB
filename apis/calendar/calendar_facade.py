from __future__ import print_function
from slack_sdk import WebClient
from .calendar_helper import *

import pytz
import schedule
import time
import argparse
import sys
import dateutil.parser
import datetime


def get_todays_events(service, calendar):
    eastern = pytz.timezone(TIMEZONE)
    now = datetime.datetime.now(eastern).isoformat()
    today = datetime.date.today()
    midnight = datetime.datetime.combine(today, datetime.time.max)
    midnight = midnight.replace(tzinfo=pytz.timezone('America/New_York'))
    midnight = midnight.isoformat()
    
    todaysResults = service.events().list(
            calendarId=calendar, timeMin=now, orderBy='startTime', singleEvents=True,
            timeMax=midnight).execute()
    todays_events = todaysResults.get('items',[])

    return todays_events   

def get_weeks_events(service, calendar):
    eastern = pytz.timezone(TIMEZONE)
    now = datetime.datetime.now(eastern).isoformat()
    today = datetime.datetime.today()
    weekday = today.isoweekday();
    this_sunday = today + datetime.timedelta(days= 7 - weekday)
    this_sunday = this_sunday.isoformat() + 'Z'

    weekResults = service.events().list(
            calendarId=calendar, timeMin=now, orderBy='startTime', singleEvents=True,
            timeMax=this_sunday).execute()
    weeks_events = weekResults.get('items',[])

    return weeks_events    

def get_months_events( service, calendar):
    eastern = pytz.timezone(TIMEZONE)
    now = datetime.datetime.now(eastern).isoformat()
    today = datetime.datetime.today()
    next_month = today.replace(day=28) + datetime.timedelta(days=4)
    end_of_month = next_month - datetime.timedelta(days=next_month.day)
    end_of_month = end_of_month.isoformat() + 'Z'
    monthResults = service.events().list(
            calendarId=calendar, timeMin=now, orderBy='startTime', singleEvents=True,
            timeMax=end_of_month).execute()
    months_events = monthResults.get('items',[])
    
    return months_events

def postNotification(token, channelID, service, calendar, timePeriod):
    events = []
    message = ""
    sc = WebClient(token=token)

    if timePeriod == "today":
        events = get_todays_events(token, channelID, service, calendar)
    elif timePeriod == "this week":
        events = get_weeks_events(token, channelID, service, calendar)
    elif timePeriod == "this month":
        events = get_months_events(token, channelID,service, calendar)

    if not events:
        period = "*_No events scheduled for " + timePeriod + " :sleepy:  _*\n"
    for event in events:
        period = "*_Here are the events happening " + timePeriod + "  :smile: _*\n"
        period = period.encode('utf-8')
        start_date = dateutil.parser.parse(event['start'].get('dateTime'))
        start_date = start_date.strftime("%A, %B %d %Y @ %I:%M %p")
        end_date = dateutil.parser.parse(event['end'].get('dateTime'))
        end_date = end_date.strftime("%A, %B %d %Y @ %I:%M %p")
        message += "\n - " + "*" + event['summary'] + "*" + "\n"+ start_date + " to " + end_date + "\n" + "*Where:* " + event['location'] + "\n" + "*Description:* " + event['description'] + "\n" + event['htmlLink'] + "\n"
        message = message.encode('utf-8')
        
    sc.api_call("chat.postMessage",username="Slack Notifier",channel=channelID,text=period + message)

def printInConsole(token, channelID, service, calendar, timePeriod):
    events = []
    message = ""

    if timePeriod == "today":
        events = get_todays_events(token, channelID, service, calendar)
    elif timePeriod == "this week":
        events = get_weeks_events(token, channelID, service, calendar)
    elif timePeriod == "this month":
        events = get_months_events(token, channelID,service, calendar)

    if not events:
        period = "No events scheduled for " + timePeriod + "\n"
    for event in events:
        period = "Here are the events happening " + timePeriod + "\n"
        start_date = dateutil.parser.parse(event['start'].get('dateTime'))
        start_date = start_date.strftime("%A, %B %d %Y @ %I:%M %p")
        end_date = dateutil.parser.parse(event['end'].get('dateTime'))
        end_date = end_date.strftime("%A, %B %d %Y @ %I:%M %p")
        message += "\n - "+ event['summary'] + "\n"+ start_date + " to " + end_date + "\n" + "Where: " + event['location'] + "\n" + "Description: " + event['description'] + "\n" + event['htmlLink'] + "\n"
    
    print(period + message)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("calendar",help="input the calendar you would like to set notifications for",type=str)
    parser.add_argument("token",help="input the token for your Slack team",type=str)
    parser.add_argument("channelID",help="input the channel you would like the bot to post in",type=str)
    parser.add_argument("-d","--daily",help="set a daily reminder",action="store_true")
    parser.add_argument("-w","--weekly",help="set a weekly reminder",action="store_true")
    parser.add_argument("-m","--monthly",help="set a monthly reminder",action="store_true")
    parser.add_argument("-dt","--displayToday",help="display today's events",action="store_true")
    parser.add_argument("-dw","--displayWeek",help="display this week's events",action="store_true")
    parser.add_argument("-dm","--displayMonth",help="display this month's events",action="store_true")
    parser.add_argument("-r","--reminder",help="set time of Slack channel event notifications (if not set, notification time defaults to midnight)",type=str)
    
    args = parser.parse_args()
   
   #set the default notification time to midnight if no notification time is entered
    notificationTime = "0:00"
    service = get_calendar_service()

   #check to see if the calendar is exists and/or the user has permission to access
    try:
        calendar = args.calendar
        cal = service.calendars().get(calendarId=calendar).execute()
    except Exception as exc:
        if exc.resp['status'] == '404':
            print("Calendar %s not found" % calendar)
        else:
            print(exc.message)
        sys.exit()
   
    if args.reminder:
        notificationTime = args.reminder
        print("Reminder set for", args.reminder)
    if args.displayToday:
        printInConsole(args.token, args.channelID, service, calendar, "today")
    if args.displayWeek:
        printInConsole(args.token, args.channelID, service, calendar, "this week")
    if args.displayMonth:
        printInConsole(args.token, args.channelID, service, calendar, "this month")
    if args.daily:
        schedule.every().day.at(notificationTime).do(postNotification, args.token, args.channelID, service, calendar, "today")
        print("Daily reminder is on")
    if args.weekly:
        schedule.every().monday.at(notificationTime).do(postNotification, args.token, args.channelID, service, calendar,"this week")
        print("Weekly reminder is on")
    if args.monthly:
        print("Monthly reminder is on")
   
   #infinite loops runs continuously to ensure daily, weekly, and monthly alerts work
    if args.daily | args.weekly | args.monthly:
        while True:
            if args.monthly:
                today = datetime.datetime.now().replace(microsecond=0)
                first_of_month = datetime.datetime(today.year, today.month, 1, 0, 0, 0)
                if today == first_of_month:
                    postNotification(args.token, args.channelID, service, calendar, "this month")
            schedule.run_pending()
            time.sleep(1)
        
if __name__ == '__main__':
    print(get_calendar_service())