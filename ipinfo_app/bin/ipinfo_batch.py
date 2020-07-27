#!/usr/bin/env python
# Splunk specific dependencies
import sys, os
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators, splunklib_logger as logger
# Command specific dependencies
import requests
import json
import splunk.appserver.mrsparkle.lib.util as splunk_lib_util

@Configuration(type='reporting')
class ipinfo(GeneratingCommand):

  url        = Option(require=False, validate=validators.Match('https url', '^https:\/\/'))
  headers    = Option(require=False)
  method     = Option(require=False, default='POST')
  ip         = Option(require=True)

  

  def generate(self):
    url        = "https://ipinfo.io/batch?token="
    headers    = self.parseHeaders("{'Content-type': 'application/json'}")
    method = "post"
    data = self.parseData(self.ip)

    record = {}

    storage_passwords=self.service.storage_passwords

    local_conf = splunk_lib_util.make_splunkhome_path(["etc","apps","ipinfo_app","local", "ip_info_setup.conf"])
    
    f_read = open(local_conf, "r")
    
    for line in f_read:
        if "token" in line:
            token = line.split("=")[1].strip()
        elif "sub" in line:
            global sub
            sub = line.split("=")[1].strip()
    f_read.close()

    url = url+token

    response = requests.request(method, url, headers=headers , data=data )
    records = response.json()
    for key,value in records.items():
        record=value
        yield record
    
  def parseHeaders(self, headers):
    # Replace single quotes with double quotes for valid json
    return json.loads(
      headers.replace('\'', '"')
    )
  
  def parseData(self, data):
    data="[\""+data+"\"]"
    return (
      data.replace(',', '","') 
    )


dispatch(ipinfo, sys.argv, sys.stdin, sys.stdout, __name__)