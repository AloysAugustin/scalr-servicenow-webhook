#!/usr/bin/env python

import binascii
import hmac
import json

from hashlib import sha1
from datetime import datetime

import requests

with open('./config.json') as f:
    data = f.read()
    signing_key = json.loads(data)['SCALR_SIGNING_KEY'].encode('ascii')

payload = """{
  "configurationId": "f257be82-f4ec-49d4-89a0-1891e25f8780",
  "data": {
    "SCALR_ACCOUNT_ID": "8",
    "SCALR_ACCOUNT_NAME": "ACME Application Development",
    "SCALR_BEHAVIORS": "base",
    "SCALR_CLOUD_LOCATION": "datacenter-21",
    "SCALR_CLOUD_PLATFORM": "vmware",
    "SCALR_CLOUD_SERVER_ID": "vm-68",
    "SCALR_COST_CENTER_BC": "CC-07",
    "SCALR_COST_CENTER_ID": "e073e2eb-f585-49b3-8eee-3e44292bc60e",
    "SCALR_COST_CENTER_NAME": "ACME Application Development",
    "SCALR_ENV_ID": "24",
    "SCALR_ENV_NAME": "Production",
    "SCALR_EVENT_ACCOUNT_ID": "8",
    "SCALR_EVENT_ACCOUNT_NAME": "ACME Application Development",
    "SCALR_EVENT_BEHAVIORS": "base",
    "SCALR_EVENT_CLOUD_LOCATION": "datacenter-21",
    "SCALR_EVENT_CLOUD_PLATFORM": "vmware",
    "SCALR_EVENT_CLOUD_SERVER_ID": "vm-68",
    "SCALR_EVENT_COST_CENTER_BC": "CC-07",
    "SCALR_EVENT_COST_CENTER_ID": "e073e2eb-f585-49b3-8eee-3e44292bc60e",
    "SCALR_EVENT_COST_CENTER_NAME": "ACME Application Development",
    "SCALR_EVENT_ENV_ID": "24",
    "SCALR_EVENT_ENV_NAME": "Production",
    "SCALR_EVENT_EXTERNAL_IP": "138.201.45.101",
    "SCALR_EVENT_FARM_HASH": "6b347c8f3a9a47",
    "SCALR_EVENT_FARM_ID": "1439",
    "SCALR_EVENT_FARM_NAME": "test",
    "SCALR_EVENT_FARM_OWNER_EMAIL": "marc@scalr.com",
    "SCALR_EVENT_FARM_ROLE_ALIAS": "ubuntu16-base",
    "SCALR_EVENT_FARM_ROLE_ID": "1978",
    "SCALR_EVENT_FARM_TEAM": "",
    "SCALR_EVENT_ID": "333d5bfa",
    "SCALR_EVENT_IMAGE_ID": "vm-41",
    "SCALR_EVENT_INSTANCE_FARM_INDEX": "1",
    "SCALR_EVENT_INSTANCE_INDEX": "1",
    "SCALR_EVENT_INTERNAL_IP": "138.201.45.101",
    "SCALR_EVENT_ISDBMASTER": "",
    "SCALR_EVENT_NAME": "HostUp",
    "SCALR_EVENT_PROJECT_BC": "PR-30",
    "SCALR_EVENT_PROJECT_ID": "f0b53e68-c47c-4c5f-868d-1358af706648",
    "SCALR_EVENT_PROJECT_NAME": "Drone Systems",
    "SCALR_EVENT_ROLE_NAME": "ubuntu16-base",
    "SCALR_EVENT_SERVER_HOSTNAME": "ubuntu",
    "SCALR_EVENT_SERVER_ID": "5bbd72c5-908c-4535-a7ec-2fbf56486ff3",
    "SCALR_EVENT_SERVER_TYPE": "0f52797dd8ba",
    "SCALR_EXTERNAL_IP": "138.201.45.101",
    "SCALR_FARM_HASH": "6b347c8f3a9a47",
    "SCALR_FARM_ID": "1439",
    "SCALR_FARM_NAME": "test",
    "SCALR_FARM_OWNER_EMAIL": "marc@scalr.com",
    "SCALR_FARM_ROLE_ALIAS": "ubuntu16-base",
    "SCALR_FARM_ROLE_ID": "1978",
    "SCALR_FARM_TEAM": "",
    "SCALR_ID": "333d5bfa",
    "SCALR_IMAGE_ID": "vm-41",
    "SCALR_INSTANCE_FARM_INDEX": "1",
    "SCALR_INSTANCE_INDEX": "1",
    "SCALR_INTERNAL_IP": "138.201.45.101",
    "SCALR_ISDBMASTER": "",
    "SCALR_PROJECT_BC": "PR-30",
    "SCALR_PROJECT_ID": "f0b53e68-c47c-4c5f-868d-1358af706648",
    "SCALR_PROJECT_NAME": "Drone Systems",
    "SCALR_ROLE_NAME": "ubuntu16-base",
    "SCALR_SERVER_HOSTNAME": "ubuntu",
    "SCALR_SERVER_ID": "5bbd72c5-908c-4535-a7ec-2fbf56486ff3",
    "SCALR_SERVER_TYPE": "0f52797dd8ba",
    "tests": "slave",
    "environment": "Development"
  },
  "endpointId": "03c8b252-1190-44c4-b9da-1074eaa215fc",
  "eventId": "a71ff7bc-0fa7-4cc2-9e0b-9fa3581888ce",
  "eventName": "HostUp",
  "timestamp": "Tue 11 Apr 2017 11:01:11 UTC",
  "userData": ""
}"""

def httpdate(dt):
    """Return a string representation of a date according to RFC 1123
    (HTTP/1.1).

    The supplied date must be in UTC.

    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
        dt.year, dt.hour, dt.minute, dt.second)

def signature(date, body):
    return binascii.hexlify(hmac.new(signing_key, body + date, sha1).digest())

date = httpdate(datetime.utcnow())
sig = signature(date, payload)

headers = {
    'Date': date,
    'X-Signature': sig
}


r = requests.post('http://localhost:80/servicenow/', headers=headers, data=payload)
print r.status_code
print r.text

