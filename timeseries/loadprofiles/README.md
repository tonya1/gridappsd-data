

Make sure influxdb is loaded 

To build bulkload file:  python3 loadprofile_measurement_bulk.py

At command prompt: influx -import -path=loadprofile_measurement_out.txt -precision s

