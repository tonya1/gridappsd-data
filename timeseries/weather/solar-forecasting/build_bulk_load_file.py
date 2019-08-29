'''
Created on Sep 21, 2018

@author: ericstephan
'''
import time, os
from datetime import datetime
from pytz import timezone

raw_input_weather_file = 'GHI_DHI_Temp_Wind_20130101_english_units_clean.csv'
bulk_load_output_file = 'ghi_dhi_bulkload.txt'
measurement = "weather"
database = "proven"
daylight_savings_time = True
override_date_dict =    {
  "newval": 2018,
  "datetype": "Y",
  "delimiter": "/"
}



def override_date(override_date_dict):
    return override_date_dict
def utc_offset(daylight):                     
    epoch_onehour = 3600
    val = epoch_onehour
    if (daylight):
        val = 3600 * 6
    else:
        val = 3600 * 7
    return val

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def process_value(s):
    if (is_number(s)):
        return s
    else:
        s = "\"" + s + "\""
    return s 
        
def strip_extra_chars(s):
        s = s.rstrip(" ")
        s = s.rstrip("\t")
        s = s.rstrip("\m")
        s = s.rstrip("\n")
        s = s.rstrip("\r")
        return s

def create_import_header_lines(database):
    s = "DROP DATABASE " + database + "\n"
    s = s + "CREATE DATABASE " + database + "\n"
    s = s + "# DML\n"
    s = s + "# CONTEXT-DATABASE: " + database + "\n"
    s = s + "# CONTEXT-RETENTION-POLICY: autogen \n\n"
    return s



def add_tags(measurement_name):
        measurement = measurement_name
        place = "Solar\ Radiation\ Research\ Laboratory"
        lat = "39.74\ N"
        long = "105.18\ W"
        tags = "place=\"" + place + "\",lat=\"" + lat + "\",long=\"" + long + "\" "
        return tags


count = 0;
title_tokens = ""
title_columns = 0
with open(raw_input_weather_file) as fin:
    for line in fin:
        line = strip_extra_chars(line)
        count = count + 1
        if (count == 2):
            title_tokens = line.split(",") 

            print(line)
            title_columns = len(title_tokens)
            break
        else:
            pass

count = 0
while (count < title_columns):
    buff  = title_tokens[count]
    buff = buff.replace(" ", "\\ ")
    title_tokens[count] = buff
    count = count + 1;

count = 0
data_columns = 0
data_tokens = ""
fo = open(bulk_load_output_file,'w')
fo.write(create_import_header_lines(database))

with open(raw_input_weather_file) as fin:
    for line in fin:
        line = strip_extra_chars(line)
        count = count + 1
        if (count > 2):
            data_tokens = line.split(",") 
            data_columns = len(data_tokens)
            if ((data_columns -1 ) != title_columns) :
                print ("ERROR:  " + line)
                print ("ERROR: " + str(data_columns) + " " + str(title_columns) + "\n")
                break
            else:
                column_counter = 0
                newline = ""
                while (column_counter < title_columns):
                    if (column_counter == 0) :
                        newline =  title_tokens[column_counter] + "=" +  process_value(data_tokens[column_counter + 1]) 
                    else: 
                        newline = newline + "," + title_tokens[column_counter] + "=" + process_value(data_tokens[column_counter + 1])
                    column_counter = column_counter + 1;
####                    newdate = process_date(data_tokens[1], override_date)
                    d=data_tokens[1] + " " + data_tokens[2] 
                    p='%m/%d/%Y %H:%M'
                    
#                    dt = datetime.fromtimestamp(time.mktime(time.strptime(d,p)))
#                    datetime.
#                   now_time = datetime.now(timezone('US/Mountain'))
                    
                    
                epoch = int(time.mktime(time.strptime(d,p))) 
                fo.write( measurement + "," + add_tags(measurement) + " " + newline + " " + str(epoch) + "\n" )
    fo.close()
