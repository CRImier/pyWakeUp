#! /usr/bin/env python

from datetime import datetime, timedelta
from threading import Thread
import logging
import os
from time import sleep


logging.basicConfig(level = logging.DEBUG)

"""# define various handy options
usage = "usage: %prog [options] [+]hours:minutes"
parser = OptionParser(usage=usage)
parser.add_option("-m", "--music", dest="music", help="Specify alarm music. May be path or number of track in known tracks list. Path is assumed relative to " + collection_location + " if relative path given, unless -r set. Default is random known track.", metavar="PATH_TO_MUSIC")
parser.add_option("-r", "--relative", dest="relative", help="Use path relative to current directory", default=False, action="store_true")
parser.add_option("-a", "--again", dest="again", help="Play a second alarm as a reminder a few minutes after the first", default=False, action="store_true")
parser.add_option("-c", "--command", help="Specify a command to play the alarm. Defaults to VLC.", default=False)
(options, args) = parser.parse_args()"""

"""while True:
    # loop until alarm time
    now = datetime.now()
    print "\rAlarm in", alarmtime - now,
    sys.stdout.flush()
    if alarmtime < now:
        # alarm time has passed, sound alarm
        print "\nGood morning, sir! It is", now, "and this is your requested wake up call."
        fred = Popen(cmd + [music])
        fred.communicate()
        break
    else:
        sleep(5)

if options.again:
    # second alarm has been requested, snooze then trigger
    end = datetime.now()
    reminder = end + timedelta(minutes=snooze_time)
    while True:
        now = datetime.now()
        if reminder < now:
            print "You should be up by now, sir. You'll be late."
            while True:
                fred = Popen(cmd + [rickroll_path])
                fred.communicate()
            break
        else:
            sleep(5)"""


class AlarmDaemon():
    set_alarms = []
    #Structure of element: [datetime object of alarm time, whatever, {whatever...}]
    #Only first element matters here, others will be preserved and can be used for alarm identification
    triggered_alarms = []
    sleep_time = 0

    on_alarm_trigger_cb = lambda self, alarm: None
    
    #Want to set a callback? Wrap around these!

    sleep_divisor = 2 #Amount by which time till next alarm is divided to get time fo daemon to sleep
    empty_check_interval = 10 #Amount of time to sleep in case there are no set alarms

    def __init__(self):
        #Being overly cautious
        self.set_alarms = [] 
        self.triggered_alarms = []

    def adjust_sleep_time(self, time_till_next_alarm):
        if time_till_next_alarm < 5:
            self.sleep_time = 1
        else:
            self.sleep_time = time_till_next_alarm/self.sleep_divisor

    def start_thread(self):
        self.thread = Thread(target=self.run)
        self.thread.daemon=True
        self.thread.start()

    def run(self):
        while True:
            self.check_alarms()
            #self.sound_triggered_alarms()
            sleep(self.sleep_time)

    def set_alarm(self, alarm):
        self.set_alarms.append(alarm)
        
    def check_alarms(self):
        logging.debug("Checking alarms...")
        now = datetime.now()
        time_till_alarms = [] #Storing all yet-to-happen times-till-alarms to see when's the next closest alarm
        for alarm in self.set_alarms[:]: 
            time_till_alarm = int((alarm[0] - now).total_seconds())
            if time_till_alarm <= 0: #Gone off!
                logging.info("Alarm happened, alarm info: {}".format(alarm[1:]))
                self.triggered_alarms.append(alarm)
                self.set_alarms.remove(alarm)
                self.on_alarm_trigger_cb(alarm)
            else:                    #Saving time only if alarm didn't happen this cycle
                logging.debug("Alarm didn't happen yet, time till alarm: {}".format(time_till_alarm))
                time_till_alarms.append(time_till_alarm) 
        if self.set_alarms:
            logging.debug("Currently set alarms: {}".format(self.set_alarms))
            logging.debug("Alarms will happen after: {}".format(time_till_alarms))
            time_till_next_alarm = min(time_till_alarms) #The lowest value from the list of times-till-alarms
            self.adjust_sleep_time(time_till_next_alarm)
            logging.debug("Set sleep time to {}".format(self.sleep_time))
        else:
            logging.debug("No alarms, will sleep for {} seconds".format(self.empty_check_interval))
            self.sleep_time = self.empty_check_interval
            
if __name__ == "__main__":
    ad = AlarmDaemon()
    ad.start_thread()
    ad.set_alarm([datetime.now()+timedelta(seconds=20), "Alarm 1"])
    ad.set_alarm([datetime.now()+timedelta(seconds=30), "Alarm 2"])
