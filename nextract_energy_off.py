#!/usr/bin/python3
version=41 # Sept 2022

import hmc_pcm as hmc
import time
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
    print('"Comment1": "other parameters are ignored",')
    print('"Comment2": "last name=value line has no ending comma"')
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
    with open(sys.argv[1]) as auth_file:
        auth = json.load(auth_file)
    hmc_hostname=auth["hmc_hostname"]
    hmc_user    =auth["hmc_user"]
    hmc_password=auth["hmc_password"]
except:
    print("Problem loading JSON file %s"%(sys.argv[1]))
    print("hmc_hostname=%s hmc_username=%s hmc_password=%s"%(hmc_hostname,hmc_user,hmc_password))
    sys.exit(0)

print("Starting %s version %d"%(sys.argv[0],version))

hmc = hmc.HMC(hmc_hostname, hmc_user, hmc_password)

#hmc.set_debug(True)

serverlist = hmc.get_server_details_pcm()  # returns a list of dictionaries one per Server

flags_need_setting = 0
for count,server in enumerate(serverlist):
    if server['capable'] == 'false':
        print("-->Server %d %-20s not capable of supplying Energy stats"%(count,server['name']))
        continue
    if server['energy'] == 'false':
        print("-->Server %d %-20s capable of collecting Enegry stats and not enabled"%(count,server['name']))
        continue
    print("-->Server %d %-20s capable of collecting Energy stats but need disabling now"%(count,server['name']))
    hmc.set_energy_flags(server['name'],'false')
    flags_need_setting += 1

if flags_need_setting > 0:
    print("->Sending updated energy preferences to the HMC")
    hmc.set_preferences_pcm()

print("-> Finished")
