'''
Created on Oct 8, 2019

@author: d3a303
''' 

import time
import os

raw_input_file = "ieeezipload.player"
measurement = "loadprofile"
bulk_load_output_file = "loadprofile_measurement_out.txt"
database = "proven"
month = 1
day = 1
year = 2018


def create_import_header_lines(database):
    s = "CREATE DATABASE " + database + "\n"
    s = s + "# DML\n"
    s = s + "# CONTEXT-DATABASE: " + database + "\n"
    s = s + "# CONTEXT-RETENTION-POLICY: autogen \n\n"
    return s

def strip_extra_chars(s):
        s = s.rstrip(" ")
        s = s.rstrip("\t")
        s = s.rstrip("\m")
        s = s.rstrip("\n")
        s = s.rstrip("\r")
        return s



def pad_number (number):
    num_str = ""
    if (number < 10):
        num_str = "0" + str(number)
    else:
        num_str = str(number)
        
    return num_str;

def next_time(hour, minute):
    next_minute = minute
    next_hour = hour
    if (minute == 59):
        next_minute = 0;
        next_hour = hour + 1
    else:
        next_minute = minute + 1
    if (hour == 23):
        if (minute == 59):
            next_hour = 0
            next_minute = 0
        else:
            next_minute = minute + 1
    return next_hour, next_minute

def next_date(year, month, day):
    next_day = day
    next_month = month
    next_year = year
    if (year % 400 == 0):
        leap_year = True
    elif (year % 100 == 0):
        leap_year = False
    elif (year % 4 == 0):
        leap_year = True
    else:
        leap_year = False
    
    
    if month in (1, 3, 5, 7, 8, 10, 12):
        month_length = 31
    elif month == 2:
        if leap_year:
            month_length = 29
        else:
            month_length = 28
    else:
        month_length = 30
    
    
    if day < month_length:
        next_day += 1
    else:
        next_day = 1
        if month == 12:
            next_month = 1
            next_year += 1
        else:
            next_month += 1
    return next_month, next_day

def process_day(month,day,year):
    hour = 0
    minute = 0
    timezone = ""
    flag =  True
    # fw = open("loadplayer.txt")
    with open(raw_input_file) as fp:
       line = fp.readline()
       line_tokens = line.split(",")
       dt_tokens = line_tokens[0].split(" ")
       if (len(dt_tokens) == 3): 
           start_date_str = dt_tokens[0]
           start_time_str = dt_tokens[1]
           timezone = dt_tokens[2]
           newline = strip_extra_chars(line_tokens[1])  

       while line:
    #       print("Line {}: {}".format(cnt, line.strip()))
           line = fp.readline()
           newline = strip_extra_chars(line)
           tokens = newline.split(",")
           if len(tokens) == 2 :
            hour,minute = next_time(hour, minute)
#            date_time = '29.08.2011 11:05:02'
            date_time = pad_number(day) + "." + pad_number(month) + "." + str(year) + " " + pad_number(hour) + ":" +  pad_number(minute) + ":00"
            pattern = '%d.%m.%Y %H:%M:%S'
            epoch = int(time.mktime(time.strptime(date_time, pattern)))
            fo.write(measurement + "," + "DATE=" + "'" + pad_number(day) +  "/" +  pad_number(month) + "/" + str(year) + "'," + "UTC='" + pad_number(hour) + ":" +  pad_number(minute) + "' value=" + tokens[1] + " " + str(epoch) + "\n") 
         
         
   
bulkload_file = bulk_load_output_file
fo = open(bulkload_file,'w')
fo.write(create_import_header_lines(database) + "\n")
for day_counter in range(1,366):
    process_day(month,day, year)
    month, day = next_date(2018, month, day)
    day_counter = day_counter + 1

fo.close()
print "created..." + bulk_load_output_file