#!/bin/bash

docker exec -it webhook-servicenow bash -c "tail -30 /var/log/supervisor/uwsgi-stderr*"
