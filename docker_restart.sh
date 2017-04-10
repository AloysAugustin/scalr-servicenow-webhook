#!/bin/bash

docker stop webhook-servicenow
docker rm webhook-servicenow
docker build -t webhook-servicenow .
docker run -p 5000:5000 -tid --name webhook-servicenow webhook-servicenow
