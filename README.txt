nextract plus 

For version 41
Code
Simplify parameted to a single .json configuration file (one per HMC)
Watts, temperature and SSP share the same database as nextract_plus
Energy handles variable number of CPU cores & Planar statistics
Code reduction for speed and reliability
New/improved Grafana dashboards
Rework nextract articles down to one article on the AIXpert Blog
Removed the clock from Dashboards

For Version 35
Code
Fixed 2 bugs where stats with multiple resources, only the last one was saved
On my servers this increased saved measurements 102K to 146K at each run but took 10% longer
Refactory the code to remove repeated code - removed 120 lines of code
Dashboard
Minor clean up
If networks stats data rate is in packets then the graph units are Packets/s. 
If storge number of reads or writes then the units are "io op/s"
Disk and networks graph first Byte/s then to the right is packets/s (or num of reads/writes per second)

For Version 34 
Code
Minor code reduction
Fix for server sriov adater stats to include all port
Added robustness code for working with older HMC code levels
Fix for LPAR vFC data - the documentation on the REST API was wrong
Fix change Python3 try: and except: handling to unlink network and storage stats
Added saveInflux=True - switch to False to stop attempts to talk to InfluxDB. You will need saveJSON to save output
- points on the 5 lines of code for InfluxDB that could be rewritten for other time-series database
Optimising, if LPAR is not Active don't botther trying to find network/storage stats

Dashboard
Dozens of improvement all over
Experimental Graphs at the end re-organised
Server SRIOV added and tested
LPAR vFC large changes and tested


For Version 32 Python code

Changed some measurement names, fixed more tags for advanced statisitics like AMS, SVIOV and some more.
Added new graphs for the above.
You must update nextract_plus.py - and sort out your usernames and passwors again, unless using the config file
I recommend dropping and creating the nextractplus InfluxDB database again as some stats changed and a bug.
You must also change to the new nextractplus v32 dashboard that matches all the new measurements names and 
  statisiscat and tags and 24 experimental graphs.
New option in the code only to switch on dumping the Line Protocol JFOS format data into a file called
  saveJSON=True to file nextractplus.json. Gzip or zip this file to massively reduce its size.
  The file is also useful for finding the measurement names and statistic names available and debugging.


For Version 31 Python code

Added tags to all the VIOS network & storage data
Added tags to LPAR network and storage data
	Includng location code and others like vlanID, vSwitchID or plain ID (name)

For  Version 31 Dashboard
Changes all Network & Storage graphs GroupBy and tag use
Changed VP:E ratio not longer percentages


For Version 21 Python code

The CPU Shared Pools added Pool ID + Pool Name
For clearer program output as it runs
For flushing data once every 25,000 records

For Version 21 the Dashboard

Added Graph Server level Shared CPU Pool with multiple pools with poolname(poolid)
Fixed and made consistent chart heading and units Read -> ReadBytes
Added VP:E Ratio for All LPARS and individual LPAR sections. Recommended 120% to 160%
Does not work with microLPARs under 1 CPU core Entitlement as Min VP=1.

Three modes set at the top of the nextract_plus.py file

mode="harcoded"
 - No change values are set in the program.
 - for different HMC's have multiple copies of the program
 - run with: ./nextract_plus.py

mode="hmc"
 - like hardcoded but a mandatory command line argument is used to set the hmc hostname
 - this assumes the saorme user and password for each HMC and these are hardcoded in the file
 - result we avoid user/passwds on the command line and ps output
 - example: ./nextract_plus.py HMC42.acme.com
 - example: ./nextract_plus.py hmc51


mode="a-file-name"
 - all hard coded values are completely ignored
 - the command line argument is the file name . I suggest a .json extension but that is not mandatory
 - example: ./nextract_plus.py hmc99.json
 - example: ./nextract_plus.py hmc100.jsom

The config file contains:
{
"hmc_hostname": "hmc15",
"hmc_username": "pcmadmin",
"hmc_password": "pcm123panda123sausages!",
"ihostname": "ultraviolet.acme.com",
"iport": 8086,
"iusername": "debbie",
"ipassword": "bladerunner808$$",
"idbname": "nextractplus"
}

All lines are needed. is not needed use ""
Remove the hashes (#)
Very sensitive to typos as this is parsed as JSON data.
Note:
    Start { and end with }
    Comma separated values but NOT after the last item
    Double quote the "strings"
    No quotes on the port number.
