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

#Jan/1/2018 00:00:00
seed_epoch_date = 1514764800
epoch_increment = 60

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


bulkload_file = bulk_load_output_file
fo = open(bulkload_file,'w')
fo.write(create_import_header_lines(database) + "\n")

epoch_index = seed_epoch_date

for day in range(1,366):
     with open(raw_input_file) as fp:
          line = fp.readline()
          while line:
               newline = strip_extra_chars(line)
               tokens = newline.split(",")
               if len(tokens) == 2 :
                    fo.write(measurement + " value=" + tokens[1] + " " + str(epoch_index) + "\n") 
               epoch_index = epoch_index + epoch_increment
               line = fp.readline()
fo.close()
print ("created..." + bulk_load_output_file)
