from datetime import timedelta
import pandas as pd
import time
from timeit import default_timer as timer

def format_seconds_to_time_string(sec,milliseconds=True):
    if milliseconds:
        time_string = pd.to_datetime(str(timedelta(seconds=sec))).strftime('%H:%M:%S.%f')
    if not milliseconds:
        time_string = pd.to_datetime(str(timedelta(seconds=sec))).strftime('%H:%M:%S')        
    return time_string


def format_milliseconds_to_time_string(milliseconds,microseconds=True):
    if microseconds:
        time_string = pd.to_datetime(str(timedelta(milliseconds=milliseconds))).strftime('%H:%M:%S.%f')
    if not microseconds:
        time_string = pd.to_datetime(str(timedelta(milliseconds=milliseconds))).strftime('%H:%M:%S')        
    return time_string


def format_time_string_to_seconds(time_string):
    time_string = str(time_string)
    try:
        milliseconds = int(time_string.split('.')[1])
    except:
        milliseconds = 0
    x = time.strptime(time_string.split('.')[0],'%H:%M:%S')
    return timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec,milliseconds=milliseconds).total_seconds()

def format_time_string_to_milliseconds(time_string):
    time_string = str(time_string)
    try:
        milliseconds = int(time_string.split('.')[1])
    except:
        milliseconds = 0

    x = time.strptime(time_string.split('.')[0],'%H:%M:%S')
    time_total = timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec,microseconds=milliseconds).total_seconds()
    return time_total*1000


def format_time_seconds_to_milliseconds(seconds):
    return seconds*1000

def format_time_milliseconds_to_seconds(milliseconds):
    return milliseconds/1000


def timer_it(time,timer):
    if time == 'start':
        start = timer()
    if time == 'end':
        end = timer()
        
        return format_milliseconds_to_time_string((end - start),True)

