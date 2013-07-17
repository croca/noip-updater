#!/usr/bin/env python
# -*- coding: utf-8 -*-
#=============================  No-ip Updater  ==============================
#
# Description: script to update you external IP address in the DDNS service
#              no-ip.com
# Author: Hector Gonzalez
# Last modified: 17/07/2013
# Version: 0.6
#
#============================================================================

# Uncomment if you don't want to manually install the requests library (not tested)
#import sys
#sys.path.append("Lib/kennethreitz-requests-2b62980")

import requests
import logging
from requests.auth import HTTPBasicAuth

class NOIP:
    USERNAME = '' # insert your noip username, e.g. myuser%40domain.com
    PASSWORD = '' # insert your password
    HOSTNAME = '' # insert your noip hostname, e.g. myuser.no-ip.org'
    WHATISMYIP = 'http://icanhazip.com' # look for your external IP address
    IPFILE = 'myIP.txt' # where to store your current IP address
    USER_AGENT = 'Python Client Updater/0.6  myusername@domain.com'
    UPDATE_URL = 'https://dynupdate.no-ip.com/nic/update'

    #init
    def __init__(self):
        try:
            f = open(self.IPFILE, 'r')
        # if IPFILE does not exist, create it
        except IOError:
            f = open(self.IPFILE, 'w')
        f.close()
    
    #getIP returns your external IP address
    def getIP(self):
        r = requests.get(self.WHATISMYIP)
        return r.text.rsplit()[0]

    # newIP looks for changes on your current IP address
    def newIP(self, IP):
        f = open(self.IPFILE, 'r')
        storedIP = f.readline()
        f.close()
        return True if storedIP != IP else False

    # refresh your external IP address in your no-ip account
    def updateIP(self, IP):
        #Build the update IP request as per no-ip instructions
        #example -> http://username:password@dynupdate.no-ip.com/nic/update?hostname=mytest.testdomain.com&myip=1.2.3.4 
        payload = {'hostname': self.HOSTNAME, 'myip':IP} #extra parameters
        
        #When making an update it is important that your http request include an HTTP User-Agent
        #to help No-IP identify different clients that access the system.
        #Clients that do not supply a User-Agent risk being blocked from the system.
        uagent = { 'user-agent': self.USER_AGENT}
        
        #execute the GET request
        r = requests.get(self.UPDATE_URL, headers=uagent, params=payload, auth=HTTPBasicAuth(self.USERNAME,self.PASSWORD))
        # Uncomment to show on console the final URL (debug only)
        #print r.url
        # Uncomment to show on console the HTTP response code 200,401,etc. (debug only)
        #print r.status_code
        # Uncomment to  show on console the headers of the HTTP response (debug only)
        #print r.headers
        return r.text.encode("ascii")

    def storeIP(self, IP):
        f = open(self.IPFILE, 'w')
        f.write(IP)
        f.close()

# end of class NOIP

# Open/Create the log file with level ERROR and timestamp enabled
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',filename='noipUpdater.log',level=logging.INFO)

# create instance of class NOIP
c = NOIP()
# if the IP has changed, call the update IP address method
IP = c.getIP()
if c.newIP(IP):
    output = c.updateIP(IP)
    # Write the success message into the log
    if output.rsplit()[0] == 'good':
        logging.info("External IP %s has been updated", IP)
        #only if the IP is successfully updated we store its value on a local file
        c.storeIP(IP)
    elif output.rsplit()[0] == 'nochg':
        logging.info("External IP %s has not changed", IP)
    # Write the possible error into the log file 
    elif output.rsplit()[0] == 'badauth':
        logging.error('Invalid username/password')
    elif output.rsplit()[0] == 'nohost':
        logging.error('No hostname specified')
    elif output.rsplit()[0] == 'badagent':
        logging.error('Client disabled. Client should exit and not perform any more updates without user intervention')
    elif output.rsplit()[0] == '!donator':
        logging.error('An update request was sent including a feature that is not available to that particular user such as offline options')
    else:
        logging.error(output)
else:
    # IP has not changed
    logging.info('External IP has not changed')
