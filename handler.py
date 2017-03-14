SCALR_SIGNING_KEY = 'enter-your-scalr-signing-key-here' 
USERNAME = 'enter-your-servicenow-username-here' 
PASSWORD = 'enter-your-servicenow-password-here' 
URL = 'https://enter-your-servicenow-domain-here/api/now/table/u_scalr_events' 
from flask import Flask
from flask import request
from flask import abort
import urllib2 
import json 
import hmac 
import binascii 
import dateutil.parser 
from hashlib import sha1 
from datetime import tzinfo, timedelta, datetime 

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
        return 'SIGNATURE ERROR'
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
    
    return response.read()
    
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