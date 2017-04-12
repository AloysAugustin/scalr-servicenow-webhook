#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

BASEDIR="$( cd $DIR/.. && pwd )"

echo "Installation directory: $BASEDIR"

cd $DIR

cp -f ./nginx.conf /opt/nginx-uwsgi/embedded/conf/nginx.conf
cat ./servicenow.ini |sed "s:<<INSTALL_DIR>>:$BASEDIR:g" > /opt/nginx-uwsgi/etc/uwsgi.d/servicenow.ini

service supervisor restart
