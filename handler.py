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


config_file = './config.json'

# Will be overridden if present in config_file
SCALR_SIGNING_KEY = ''
USERNAME = ''
PASSWORD = ''
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
    
    values = {'u_event': body['eventName'], 'u_event_id': body['eventId'], 'u_payload': request.data }
    
    headers = {'Content-Type': 'application/json'}
    
    data = json.dumps(values).encode('utf8')
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, URL, USERNAME, PASSWORD)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    req = urllib2.Request(URL, data, headers)
    response = urllib2.urlopen(req)
    response_text = response.read()
    logging.debug(response_text)
    return response_text
    

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

loadConfig(config_file)
logging.basicConfig(level=logging.INFO)
