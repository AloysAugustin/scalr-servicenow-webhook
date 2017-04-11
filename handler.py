#!/usr/bin/env python

from flask import Flask
from flask import request
from flask import abort
import urllib2 
import json
import logging
import hmac 
import binascii 
import dateutil.parser 
from hashlib import sha1 
from datetime import tzinfo, timedelta, datetime 
import suds
from suds.client import Client

config_file = './config.json'

# Will be overridden if present in config_file
SCALR_SIGNING_KEY = ''
USERNAME = ''
PASSWORD = ''
PROXY = None
URL = ''


ZERO = timedelta(0) 

app = Flask(__name__)

class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return ZERO 

utc = UTC() 

@app.route("/servicenow/", methods=['POST'])
def lambda_handler():

    if not validateRequest(request):
        abort(403)
    body = json.loads(request.data)
    data = body["data"]
    
    client = Client(URL, username=USERNAME, password=PASSWORD, proxy=PROXY)
    server = client.factory.create('ns0:insert')

    server.company = "VistraEnergy"
    server.department = ""
    server.dns_domain = ""
    server.install_date = datetime.now(utc).isoformat()
    server.u_tentative_deploy_date = ""
    server.ip_address = get_ip(data)
    server.location = data["SCALR_CLOUD_LOCATION"]
    server.mac_address = ""
    server.manufacturer = ""
    server.name = data["SCALR_SERVER_HOSTNAME"]
    server.owned_by = data["SCALR_EVENT_FARM_OWNER_EMAIL"]
    server.short_description = "Server managed by Scalr, Account: {}, Environment: {}, Farm: {}".format(
                                data["SCALR_ACCOUNT_NAME"],
                                data["SCALR_ENV_NAME"],
                                data["SCALR_FARM_NAME"])
    server.start_date = datetime.now(utc).isoformat()
    server.u_configured_memory = get_mem(data)
    server.u_decommission_date = ""
    server.u_disk_space_gb = ""
    server.u_environment = ""
    server.u_model_version = ""
    server.u_number_of_disk_drives = ""
    server.u_number_of_processor = get_cpu(data)
    server.u_operating_system = ""
    server.u_regulatory_compliance = ""
    server.u_os_version = ""
    server.u_project_number = ""
    server.u_tier_level = ""
    server.u_vcpu = ""
    server.u_core = ""
    server.install_status = ""
    server.u_substatus = ""


    client.service.insert(server)
    return 'Ok'
    
def get_ip(data):
    if data['SCALR_EVENT_INTERNAL_IP']:
        return data['SCALR_EVENT_INTERNAL_IP']
    else:
        return data['SCALR_EVENT_EXTERNAL_IP']

vmware_instance_types = {
    # name : [vcpu, memory]
    "micro" : ["1", "1024MB"],
    "small" : ["2", "2048MB"],
    "medium" : ["4", "4096MB"],
    "large" : ["8", "8192MB"]
}

def get_cpu(data):
    if data["SCALR_CLOUD_PLATFORM"] == "vmware":
        return vmware_instance_types.get(data["SCALR_SERVER_TYPE"], ["N/A", "N/A"])[0]
    else:
        return "N/A"

def get_mem(data):
    if data["SCALR_CLOUD_PLATFORM"] == "vmware":
        return vmware_instance_types.get(data["SCALR_SERVER_TYPE"], ["N/A", "N/A"])[1]
    else:
        return "N/A"

def validateRequest(request):
    if not 'X-Signature' in request.headers or not 'Date' in request.headers:
        return False
    date = request.headers['Date']
    body = request.data
    expected_signature = binascii.hexlify(hmac.new(SCALR_SIGNING_KEY, body + date, sha1).digest())
    if expected_signature != request.headers['X-Signature']:
        return False
        
    date = dateutil.parser.parse(date)
    now = datetime.now(utc)
    delta = abs((now - date).total_seconds())
    return delta < 300


def loadConfig(filename):
    with open(config_file) as f:
        options = json.loads(f.read())
        for key in options:
            if key in ['USERNAME', 'PASSWORD', 'URL']:
                logging.info('Loaded config: {}'.format(key))
                globals()[key] = options[key]
            elif key in ['SCALR_SIGNING_KEY']:
                logging.info('Loaded config: {}'.format(key))
                globals()[key] = options[key].encode('ascii')
            elif key == 'PROXY' and options[key]:
                globals()[key] = {'http': options[key], 'https': options[key]}

loadConfig(config_file)
logging.basicConfig(level=logging.INFO)
