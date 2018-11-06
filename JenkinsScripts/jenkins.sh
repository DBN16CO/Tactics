#!/bin/bash

set -e

echo "---------------------------------------"
echo "     SETTING UP TEST ENVIRONMENT       "
echo "---------------------------------------"

if ! [ -x "$(command -v python)" ]; then
	sudo apt-get update
	sudo apt-get install -y python-dev
fi

if ! [ -x "$(command -v pip)" ]; then
	sudo apt-get update
	curl -O https://bootstrap.pypa.io/get-pip.py
    sudo python get-pip.py
fi

if ! [ -x "$(command -v virtualenv)" ]; then
	sudo pip install virtualenv
fi

if ! [ -x "$(command -v docker)" ]; then
	curl -sSL get.docker.com | sh
fi

if ! [ -x "$(command -v kubectl)" ]; then
	curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
  	echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
  	sudo apt-get update -q
  	sudo apt-get install -qy kubectl
fi

sudo apt-get install -y libpq-dev build-essential openssl-dev

virtualenv ./env
source ./env/bin/activate

pip install -r ./Server/requirements.txt

kubectl apply -f ./JenkinsScripts/postgres.yml
kubectl rollout status deploy/postgres

echo "Waiting for postgres to start"
sleep 15

PG_IP=`kubectl get svc --namespace jenkins postgres -o jsonpath="{.spec.clusterIP}"`

kubectl apply -f ./JenkinsScripts/redis.yml
kubectl rollout status deploy/redis

echo "Waiting for redis to start"
sleep 15

REDIS_IP=`kubectl get svc --namespace jenkins redis -o jsonpath="{.spec.clusterIP}"`

echo "Deployed Postgres with ip $PG_IP"
echo "Deployed Redis with ip $REDIS_IP"

echo "import dj_database_url" > ./Server/Server/localsettings.py
echo "DATABASES = {}" >> ./Server/Server/localsettings.py
echo "DATABASES['default'] =  dj_database_url.parse('postgres://postgres:test@${PG_IP}:5432/postgres')" >> ./Server/Server/localsettings.py
echo "BROKER_URL = 'redis://${REDIS_IP}:6379'" >> ./Server/Server/localsettings.py
echo "CELERY_RESULT_BACKEND = 'redis://${REDIS_IP}:6379'" >> ./Server/Server/localsettings.py
echo "CHANNEL_LAYERS = {
    'default': {
        #'BACKEND': 'asgiref.inmemory.ChannelLayer',
        'BACKEND': 'asgi_redis.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('${REDIS_IP}', 6379)],
        },
        'ROUTING': 'Server.router.channel_routing',
    },
}" >> ./Server/Server/localsettings.py
echo "Created local test settings"

echo "---------------------------------------"
echo "         RUNNING UNIT TESTS            "
echo "---------------------------------------"

pushd ./Server
coverage run manage.py test
rc=$?

popd
kubectl delete -f ./JenkinsScripts/postgres.yml
kubectl delete -f ./JenkinsScripts/redis.yml

cat ./Server/trace.log
if [ "$rc" -ne "0" ]; then
	echo "---------------------------------------"
	echo "            TESTS FAILED               "
	echo "---------------------------------------"
	exit 1
fi

echo "---------------------------------------"
echo "            TESTS PASSED               "
echo "---------------------------------------"

rm -f ./Server/Server/localsettings.py
rm -f ./Server/Server/localsettings.pyc
echo ""
