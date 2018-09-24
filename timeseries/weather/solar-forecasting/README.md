

Make sure influxdb is loaded 

To build bulkload file:  python3 build_bulk_load_file.py

At command prompt: influx -import -path=ghi_dhi_bulkload.txt -precision ms

