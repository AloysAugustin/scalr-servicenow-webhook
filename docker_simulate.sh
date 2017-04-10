#!/bin/bash

docker exec -it webhook-servicenow bash -c "cd /opt/webhook && python simulate-webhook-call.py"