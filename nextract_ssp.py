#!/usr/bin/python3
version=41 # Sept 2022

debug=True

import hmc_pcm
import nchart
import sys
import json
import time

def hint():
    print('Usage:  %s version %d'%(sys.argv[0],version))
    print('%s filename.json - use the JSON file to find the parameters'%(sys.argv[0]))
    print('Example config.json')
    print('{')
    print('"hmc_hostname": "hmc15",')
    print('"hmc_username": "pcmadmin",')
    print('"hmc_password": "panda123sausages!",')
    print('"output_nchart": 0,')
    print('"output_json": 0,')
    print('"output_csv": 0,')
    print('"comment1": "Valid setting for output_influx = 0 (off), 1 or 2",')
    print('"output_influx": 1,')
    print('"comment2": "InfluxDB 1.x options",')
    print('"ihost": "myinflux",')
    print('"iport": "8086",')
    print('"idbname": "nextractplus",')
    print('"iuser": "fred",')
    print('"ipassword": "blogs",')
    print('"comment3": "InfluxDB 2.x options",')
    print('"iurl": "https://influx.acme.com:8086",')
    print('"ibucket": "default",')
    print('"iorg": "IBM",')
    print('"itoken": "123456780..abcdefg_etc.",')
    print('"comment4": "other parameters are ignored",')
    print('"comment5": "last name=value line has no ending comma"')
    print('}')
    sys.exit(0)

if len(sys.argv) == 1:
    hint()

if len(sys.argv) != 2:
    hint()

hmc_hostname="not-found"
hmc_user    ="not-found"
hmc_password="not-found"

try:
    print("%s opening config file:%s"%(sys.argv[0], sys.argv[1]))
    with open(sys.argv[1]) as auth_file:
        auth = json.load(auth_file)
    hmc_hostname=auth["hmc_hostname"]
    hmc_user    =auth["hmc_user"]
    hmc_password=auth["hmc_password"]
except:
    print("Problem loading JSON file %s"%(sys.argv[1]))
    print("hmc_hostname=%s hmc_username=%s hmc_password=%s"%(hmc_hostname,hmc_user,hmc_password))
    sys.exit(0)

output_nchart=9
output_json=9
output_csv=9
output_influx=9

try:
    output_nchart=auth["output_nchart"]
    output_json=auth["output_json"]
    output_csv=auth["output_csv"]
    output_influx=auth["output_influx"]
except:
    print("Problem loading JSON file %s"%(sys.argv[1]))
    print("nchart=%d json=%d csv=%d influx-version=%d"
            %(output_nchart, output_json, output_csv, output_influx))
    sys.exit(0)

if output_influx == 1:
    ihost="not-found"
    iport=8086
    idbname="not-found"
    iuser="not-found"
    ipassword="not-found"

    try:
        ihost=auth["ihost"]
        iport=auth["iport"]
        idbname=auth["idbname"]
        iuser=auth["iuser"]
        ipassword=auth["ipassword"]
    except:
        print("Problem loading JSON file %s Influx1"%(sys.argv[1]))
        print("ihost=%s iport=%d idbname=%s iuser=%s ipassword=%s"
                %(ihost, iport, idbname, iuser, ipassword))
        sys.exit(0)


if output_influx == 2:
    iurl="not-found"
    ibucket="not-found"
    iorg=8086
    itoken="not-found"

    try:
        iurl=auth["iurl"]
        ibucket=auth["ibucket"]
        iorg=auth["iorg"]
        itoken=auth["itoken"]
    except:
        print("Problem loading JSON file Influx=2%s"%(sys.argv[1]))
        print("iurl=%s ibucket iorg=%d =%s itoken=%s"
                %(iurl, ibucket, iorg, itoken))
        sys.exit(0)


# - - - - 
print("-> Logging on to %s as user %s" % (hmc_hostname,hmc_user))
hmc = hmc_pcm.HMC(hmc_hostname, hmc_user, hmc_password)

print("-> Get Stripped Preferences") # returns XML text
prefstripped = hmc.get_stripped_preferences_ssp()

print("-> Parse Preferences")
ssplist = hmc.parse_prefs_ssp(prefstripped)  # returns a list of dictionaries one per SSP
all_true = True
enabled = []
for ssp in ssplist:
    if ssp['agg'] == 'false' or ssp['mon'] == 'false':
        good = "BAD "
        all_true = False
    else: 
        good = "GOOD"
        enabled.append(ssp)
    print('-> cluster=%-10s pool=%-10s AggregrateEnabled=%5s Monitoring Enabled=%5s =%s' 
        %(ssp['cluster'], ssp['pool'], ssp['agg'], ssp['mon'], good))
if all_true:
    print("-> Skipping Set Preferences as all SSP's are already enabled")
else:
    print("-> Set Preferences - please wait 10+ minutes for stats to appear!")
    prefset = hmc.set_preferences_ssp(prefstripped) # Switches on ALL Aggregatation &  monitoring flags

print("-> Processing SSP")
for count, ssp in enumerate(enabled,start=1):
    print('--> SSP=%d Getting filenames for cluster=%s pool=%s' %(count,ssp['cluster'], ssp['pool']))
    print("---> Requesting %s as monitoring enabled" %(ssp['pool']))
    starttime = time.time()
    JSONfiles = hmc.get_filenames_ssp(ssp['uuid'],ssp['pool']) # returns XML of filename(s)
    if(debug):
        hmc.save_to_file("ssp_JSONfiles.list",str(JSONfiles))
    endtime = time.time()
    print("---> Received %d file(s) in %.2f seconds" % (len(JSONfiles), endtime - starttime))
    for num,JSONfile in enumerate(JSONfiles,start=1):
        if(debug):
            hmc.save_to_file("ssp_JSONfile.json",str(JSONfile))
        print('---> File=%d Getting stats from %s' %(num,JSONfile['filename']))
        JSONdata = hmc.get_stats(JSONfile['url'],JSONfile['filename'], ssp['pool']) # returns JSON stats
        if(debug):
            hmc.save_to_file("ssp_JSONdata.json",str(JSONdata))
        print("SSP stats JSONdata size %d"%(len(JSONdata)))
        #DEBUG DUMP
        #print(JSONdata)
        info = hmc.extract_ssp_info(JSONdata)
        if(debug):
            hmc.save_to_file("ssp_SSPinfo.json",str(info))
        print("SSP info size %d"%(len(info)))
        print(info)
        sspstats = hmc.extract_ssp_totals(JSONdata)
        if(debug):
            hmc.save_to_file("ssp_SSPstats.json",str(sspstats))
        print("SSPstats size %d"%(len(sspstats)))
        #DEBUG DUMP
        #print(sspstats)
        if len(sspstats) == 0:
            print("No SSP level stats from extract_ssp_totals - bailing out on this SSP")
            continue # Do not attempt to create an empty graph
        
        header, viosstats = hmc.extract_ssp_vios(JSONdata)
        if(debug):
            hmc.save_to_file("ssp_VIOSstats.json",str(viosstats))
        print("VIOSstats size %d"%(len(viosstats)))
        if len(viosstats) == 0:
            print("No data returned from extract_ssp_vios()")
            continue # Do not attempt to create an empty graph
        #print(header)
        #print(viosstats)
        print("---> Processing JSON data size=%d bytes" % (len(JSONdata)))

        if output_csv == 1:
            filename="SSP-totals-" + info["cluster"] + "-" + info["ssp"] + ".csv"
            f = open(filename,"w")
            f.write("time, size, free, readBytes, writeBytes, readServiceTime-ms, writeServiceTime-ms\n")
            for s in sspstats:
                 buffer="%s, %d,%d, %d,%d, %.3f,%.3f\n" % (s['time'],
                        s['size'],           s['free'], 
                        s['readBytes'],      s['writeBytes'], 
                        s['readServiceTime'],s['writeServiceTime'])
                 f.write(buffer)
            f.close()
            print("Saved SSP Totals comma separated values to %s" % (filename))

            filename="SSP-VIOS-" + info["cluster"] + "-" + info["ssp"] + ".csv"
            f = open(filename,"w")
            f.write("time")
            for viosname in header:
                 f.write("," + viosname)
            f.write("\n")
            for row in viosstats:
                 f.write("%s" % (row["time"]))
                 for readkb in row['readKB']:
                     f.write(",%.3f" % (readkb))
                 for writekb in row['writeKB']:
                     f.write(",%.3f" % (writekb))
                 f.write("\n")
            f.close()
            print("Saved SSP VIOS comma separated values to %s" % (filename))

        if output_nchart:                                              # Create .html file that graphs the stats
            filename = "SSP-" + info['ssp'] + ".html"          # Using googlechart
            print("-->File=%s Length: info=%d sspstats=%d header=%d viosstats=%d" %(filename,len(info),len(sspstats),len(header),len(viosstats)))
            #print(sspstats[0])
            n = nchart.nchart_open()
            n.nchart_ssp(filename, info, sspstats, header, viosstats)
            print("Saved webpage to %s" % (filename))

        if output_influx == 1:     # push in to InfluxDB
            print("SSP for Influx 1 (Pool:%s Cluster:%s)"%(info['ssp'],info['cluster']))
            from influxdb import InfluxDBClient
            client = InfluxDBClient(ihost, iport, iuser, ipassword, idbname)

        if output_influx == 2:     # push in to InfluxDB
            print("SSP for Influx 2 (Pool:%s Cluster:%s)"%(info['ssp'],info['cluster']))
            from influxdb import InfluxDBClient
            client = InfluxDBClient(url=iurl, org=iorg, token=itoken)
            write_api = client.write_api()

        if output_influx == 2 or output_influx == 1:     # push in to InfluxDB
            entry=[]
            ssp_records=0
            vios_records=0
            #print(info)
                #{'ssp': 'spiral', 'end': '2019-07-03T15:30:00+0000', 'cluster': 'spiral', 'start': '2019-07-02T14:00:00+0000', 'frequency': 300}
            #print('sspstats')
                #{'writeServiceTime': 0.0, 'free': 247812.0, 'size': 523776.0, 'numOfWrites': 0.0, 'readBytes': 0.0, 'time': '2019-07-02T14:00:00', 'readServiceTime': 0.0, 'numOfReads': 0.0, 'writeBytes': 0.0}
            #print(sspstats)
            #print('viosstats')
            #print(viosstats)
                #['rubyvios3-Read-KBs', 'rubyvios4-Read-KBs', 'yellowvios1-Read-KBs', 'yellowvios2-Read-KBs', 'rubyvios3-Write-KBs', 'rubyvios4-Write-KBs', 'yellowvios1-Write-KBs', 'yellowvios2-Write-KBs']
            #print('header')
            #print(header)
                #{'writeKB': [0.0, 0.0, 0.0, 0.0], 'time': '2019-07-02T14:00:00', 'readKB': [0.0, 0.0, 0.0, 0.0]}
            # DEBUG DUMP
            #print("processing")
            for sam in sspstats:
                data = { 'measurement': 'SSP', 'tags': { 'pool': info['ssp'], 'cluster': info['cluster'] }, 'time': sam['time'] }
                #DENUG DUMP
                #print(data)
                data['fields'] = { "free": sam['free'],
                "size": sam['size'],
                "readBytes": sam['readBytes'],
                "writeBytes": sam['writeBytes'],
                "numOfWrites": sam['numOfWrites'],
                "numOfReads": sam['numOfReads'],
                "readServiceTime": sam['readServiceTime'],
                "writeServiceTime": sam['writeServiceTime'] }
                print(data)
                ssp_records = ssp_records +1
                entry.append(data)

            if output_influx == 1:
                client.write_points(entry)

            if output_influx == 2:
                write_api.write(ibucket, iorg, entry)

            print("Header=%s"%(header))
            half = len(header) / 2
            for sam in viosstats:
                for count,vios in enumerate(header):
                    if count >= half:
                        break
                    name=header[count]
                    name=name[0:-8]
                    if name[-1:] == '-':
                       name=name[0:-1]
                    data = { 'measurement': 'SSPVIOS', 'tags': { 'pool': info['ssp'], 'cluster': info['cluster'], 'vios': name}, 'time': sam['time'] }
                    #print(data)
                    data['fields'] = { "readKB": sam['readKB'][count], "writeKB": sam['writeKB'][count] }
                    print(data)
                    vios_records = vios_records +1
                    entry.append(data)
            if output_influx == 1:
                client.write_points(entry)

            if output_influx == 2:
                write_api.write(ibucket, iorg, entry)

print("Processed Influx SSP %d and VIOS %d records"%(ssp_records,vios_records))

print("Logging off the HMC")
hmc.logoff()
