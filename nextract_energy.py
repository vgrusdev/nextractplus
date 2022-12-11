#!/usr/bin/python3
version=41 # Sept 2022

import hmc_pcm
import nchart
import sys
import json

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

output_nchart=0 # 0 = off, 1 = on
output_json=0   # 0 = off, 1 = on
output_csv=0    # 0 = off, 1 = on
output_influx=0 # 0 = off, 1 = InfluxDB v1 or 2 = InfluxDB v2

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
        print("iurl=%s ibucket=%s iorg=%s itoken=%s"
                %(iurl, ibucket, iorg, itoken))
        sys.exit(0)

# - - - - - 
print("-> Logging on to %s as user %s" % (hmc_hostname,hmc_user))
hmc = hmc_pcm.HMC(hmc_hostname, hmc_user, hmc_password)                      # Log on to the HMC
# debugging hmc.set_debug(True)
serverlist = hmc.get_server_details_pcm()                        # Get list of attached Managed Servers dictionary

for count, server in enumerate(serverlist,start=1):              # Loop through the Servers
    if server['capable'] == 'false':
        print("-->Server %d %s not capable of supplying energy stats"%(count,server['name']))
        continue
    if server['energy'] == 'false':
        print("-->Server %d %s is energy stats capable but not enabled"%(count,server['name']))
        continue
    print("-->Server %d %s collecting Energy stats"%(count,server['name']))
    JSONdata = hmc.get_energy(server['atomid'],server['name'])   # get the stats for this Server
    if JSONdata == None:
        continue
    info = hmc.extract_energy_info(JSONdata)                     # converts JSON into summary info
    print("-->Summary:")
    print(info)
    headline,stats = hmc.extract_energy_stats(JSONdata)          # watts+temp stats as a list of dictionaries

    # print("headerline=[%s]"%(str(headline)))
    # print("stats=[%s]"%(str(stats)))

    servername = server['name']
    if output_nchart:      # Create .html file that graphs the stats
        filename = "Energy-" + servername + ".html"          # Using googlechart
        print("Create %s" %(filename))
        n = nchart.nchart_open()
        n.nchart_energy(filename, info, stats)
        print("Saved webpage to %s" % (filename))

    if output_json:       # print the dictionary
        filename = "Energy-" + servername + ".json"
        f = open(filename,"w")
        for s in stats:
            f.write(str(s))
            f.write("\n")
        f.close()
        print("Saved JSON to %s" % (filename))

    if output_csv:       # Create comma separated values file
        filename = "Energy-" + server['name'] + ".csv"
        f = open(filename,"w")
        f.write("%s\n" %(headline))
        for s in stats:
            count=0
            for key, value in s.items():
                if count == 0:
                    f.write(str(value))
                else:
                    f.write(',' + str(value))
                count = count + 1
            f.write('\n')
        f.close()
        print("Saved comma separated values to %s" % (filename))

    if output_influx == 1 or output_influx == 2:    # Create comma separated values file,old version

        if output_influx == 1:
            from influxdb import InfluxDBClient
            client = InfluxDBClient(ihost, iport, iuser, ipassword, idbname)

        if output_influx == 2:
            from influxdb import InfluxDBClient
            client = InfluxDBClient(url=iurl, org=iorg, token=itoken)
            write_api = client.write_api()

        print("Energy for Influx (%s)"%(server['name']))
        entry=[]
        count=0
        for sam in stats:
            #if count == 0:
            #    print(sam)
            data = "{ 'measurement': 'electricity','tags': { 'servername': '%s' }, 'time': '%s', 'fields': {"%(servername,sam["time"])
            data = data + ' "watts": %s,'%(sam['watts'])
            count = count +1
            data = data[:-1]
            data = data + '} }'
            d=eval(data)
            entry.append(d)
        for sam in stats:
            data = "{ 'measurement': 'temp_room','tags': { 'servername': '%s' }, 'time': '%s', 'fields': {"%(servername,sam["time"])
            data = data + ' "temp": %s,'%(sam['inlet'])
            count = count +1
            data = data[:-1]
            data = data + '} }'
            d=eval(data)
            entry.append(d)

        for sam in stats:
            n = 0
            data = "not set"
            #print(sam)
            for item in sam:
                try:
                    thiscpu='cpu'+str(n)
                    thiscpu3='cpu%03d'%(n) # 3 digit number for ordering on Grafana, cpu6 becomes cpu006
                    thistemp=sam[thiscpu]
                    #print("name="+thiscpu)
                    #print("temp="+str(thistemp))
                    data = "{ 'measurement': 'temp_processor','tags': { 'servername': '%s', 'cpu_name': '%s' }, 'time': '%s', 'fields': { 'temp': %f } }"%(servername, thiscpu3, sam["time"], thistemp)
                    d=eval(data)
                    entry.append(d)
                    count = count +1
                except:
                    pass

                try:
                    thismb='mb'+str(n)
                    thismb3='mb%03d'%(n) # 3 digit number for ordering on Grafana
                    thistemp=sam[thismb]
                    data = "{ 'measurement': 'temp_planar','tags': { 'servername': '%s', 'mb_name': '%s' }, 'time': '%s', 'fields': { 'temp': %f } }"%(servername, thismb3, sam["time"], thistemp)
                    d=eval(data)
                    #print(d)
                    entry.append(d)
                    count = count +1
                except:
                    pass
                n = n + 1 

        if len(entry) > 0:
            if output_influx == 1:
                client.write_points(entry)

            if output_influx == 2:
                write_api.write(ibucket, iorg, entry)

        print("Influx server=%s added %d records at %s"%(server['name'],count,sam["time"]))
