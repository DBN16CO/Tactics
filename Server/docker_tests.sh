#!/bin/bash

echo "Checking if this commit changed requirements.txt..."
diff /tmp/requirements.txt ./requirements.txt
rc=$?

if [ "$rc" != "0" ]; then
	echo "Requirements.txt has changed"
	pip install -r ./requirements.txt
	rc=$?
	if [ "$rc" != "0" ]; then
		echo "Failed to install newly changed requirements.txt!"
		exit 1
	fi
else
	echo "Requirements.txt has not changed"
fi

service postgresql start
/etc/init.d/redis-server start
echo "create database tactics" | sudo -u postgres psql
echo "ALTER USER postgres WITH PASSWORD 'abc12345'" | sudo -u postgres psql

coverage run ./manage.py test
rc=$?

#cat trace.log
exit $rc