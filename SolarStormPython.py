# Solar Flares - Retrieve GOES flare event list 
# The GOES daily flare lists represent the events registered 
# by GOES satellite. 
# Currently only X-Ray activity events are considered
# Using sunpy. For more info go to https://docs.sunpy.org/ 

from sunpy.net import Fido
from sunpy.net import attrs as a


event_type = "FL"
tstart = "2024/05/07"
tend = "2024/05/15"
result = Fido.search(a.Time(tstart, tend),
                     a.hek.EventType(event_type),
                     a.hek.FL.GOESCls > "C3.0",
                     a.hek.OBS.Observatory == "GOES")

# Here we only show two columns due there being over 
# 100 columns returned normally.
#print(result.show("hpc_bbox", "refs"))

# It"s also possible to access the HEK results from the
# `~sunpy.net.fido_factory.UnifiedResponse` by name.
hek_results = result["hek"]

# We only print every 10th key to avoid the output being too long.
#print(hek_results.colnames[::10])

filtered_results = hek_results["event_starttime", "event_peaktime",
                               "event_endtime", "fl_goescls", 'hpc_radius',
                               "ar_noaanum"]

#print(type(filtered_results))

results_pandas = filtered_results.to_pandas()
print(type(results_pandas))

# Sorting is done by using the flare class from "fl_goescls"
# By converting the flare class to a number using ord()
# and adding the flare strength, we can sort by value
by_magnitude = sorted(filtered_results, 
                      key=lambda x: ord(x['fl_goescls'][0]) + float(x['fl_goescls'][1:]), 
                      reverse=True)

for flare in by_magnitude:
    print(f"Class {flare['fl_goescls']} occurred on {flare['event_starttime']}")

# Let’s grab GOES XRS data for a particular time of interest and the 
# HEK flare data for this time from NOAA. 
# Here we are searching for data from the GOES-16 satellite 
# and for the 1-min average time-sampled data.
tr = a.Time('2024-05-11 01:00', '2024-05-11 23:00')
results16 = Fido.search(tr, a.Instrument.xrs & a.goes.SatelliteNumber(16) & a.Resolution("avg1m") | a.hek.FL & (a.hek.FRM.Name == 'SWPC'));

# We will now use TimeSeries data
from sunpy.timeseries import TimeSeries

## Additional code to prevent warning messages in Windows
import asyncio, sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Download the XRS data and load it into a TimeSeries, convert to a 
# dataframe for easier manipulation, and find the max values
files = Fido.fetch(results16)
goes = TimeSeries(files)
goes_data = goes.to_dataframe()

max_xrsa = goes_data['xrsa'].max()
max_xrsb = goes_data['xrsb'].max()



