#!/usr/bin/env python

from flask import Flask
from flask import request
from flask import abort
import urllib2 
import json
import logging
import hmac 
import binascii 
import random
import dateutil.parser 
from hashlib import sha1 
from datetime import tzinfo, timedelta, datetime 
import suds
from suds.client import Client

config_file = './config.json'

# Configuration settings, will be overridden if present in config_file
SCALR_SIGNING_KEY = ''
USERNAME = ''
PASSWORD = ''
PROXY = None
URL = ''

app = Flask(__name__)

# UTC timezone description
ZERO = timedelta(0)
class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return ZERO 

utc = UTC() 

# suds monkey-patching for compatibility woth python 2.6
class TestClient(suds.client.SoapClient):
    def failed(self, binding, error):
        raise error

suds.client.SoapClient = TestClient

# handler code
@app.route("/servicenow/", methods=['POST'])
def lambda_handler():

    if not validateRequest(request):
        abort(403)
    body = json.loads(request.data)
    data = body["data"]
    
    client = Client(URL, username=USERNAME, password=PASSWORD, proxy=PROXY)
    server = client.factory.create('ns0:insert')

    server.company = "Energy Future Holdings Co"
    server.department = data["SCALR_ACCOUNT_NAME"]
    server.dns_domain = "tceh.net"
    server.install_date = datetime.now(utc).isoformat()
#    server.u_tentative_deploy_date = datetime.now(utc).isoformat()
    server.ip_address = get_ip(data)
    server.location = "Mesquite Data Center"
    server.mac_address = random_mac()
    server.manufacturer = "VMware"
    server.name = data["SCALR_SERVER_HOSTNAME"]
    server.owned_by = data["SCALR_EVENT_FARM_OWNER_EMAIL"].split('@')[0]
    server.short_description = "Server managed by Scalr, Account: {0}, Environment: {1}, Farm: {2}".format(
                                data["SCALR_ACCOUNT_NAME"],
                                data["SCALR_ENV_NAME"],
                                data["SCALR_FARM_NAME"])
    server.start_date = datetime.now(utc).isoformat()
    server.u_configured_memory = get_mem(data)
    server.u_decommission_date = ""
    server.u_disk_space_gb = "100"
    server.u_environment = data["SCALR_ENV_NAME"]
    server.u_model_version = "vmx-08"
    server.u_number_of_disk_drives = "1"
    server.u_number_of_processor = get_cpu(data)
    server.u_operating_system = "Linux"
    server.u_regulatory_compliance = ""
    server.u_os_version = "Red Hat Enterprise Linux 6 (64-bit)"
    server.u_project_number = ""
    server.u_tier_level = "4"
    server.u_vcpu = get_cpu(data)
    server.u_core = get_cpu(data)
    server.install_status = "-1"
    server.u_substatus = "Build"
    print server

    try:
        print client.service.insert(server)
        print client.last_received()
        return 'Ok'
    except Exception:
        logging.exception('Servicenow request failed')
        raise
    
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

def random_mac():
    return "52:54:00:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        )

def total_seconds(dt):
     # Keep backward compatibility with Python 2.6 which doesn't have
     # this method
     if hasattr(dt, 'total_seconds'):
         return dt.total_seconds()
     else:
         return (dt.microseconds + (dt.seconds + dt.days * 24 * 3600) * 10**6) / 10**6


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
    delta = abs(total_seconds(now - date))
    return delta < 300


def loadConfig(filename):
    with open(config_file) as f:
        options = json.loads(f.read())
        for key in options:
            if key in ['USERNAME', 'PASSWORD', 'URL']:
                logging.info('Loaded config: {0}'.format(key))
                globals()[key] = options[key]
            elif key in ['SCALR_SIGNING_KEY']:
                logging.info('Loaded config: {0}'.format(key))
                globals()[key] = options[key].encode('ascii')
            elif key == 'PROXY' and options[key]:
                globals()[key] = {'http': options[key], 'https': options[key]}

loadConfig(config_file)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
