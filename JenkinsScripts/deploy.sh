#!/bin/bash

set -e

echo "---------------------------------------"
echo "     SETTING UP DEPLOY ENVIRONMENT     "
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

sudo apt-get install -y libpq-dev build-essential libssl-dev libffi6 libffi-dev

virtualenv ./env
source ./env/bin/activate

pip install -r ./Server/requirements.txt

echo "---------------------------------------"
echo "        BUILDING DOCKER IMAGE          "
echo "---------------------------------------"

sudo docker build -t tactics:latest .
sudo docker tag tactics:latest localhost:5000/tactics

echo "---------------------------------------"
echo "        PUSHING DOCKER IMAGE           "
echo "---------------------------------------"

sudo docker push localhost:5000/tactics
sudo docker rmi tactics:latest

echo "---------------------------------------"
echo "        MIGRATING POSTGRES DB          "
echo "---------------------------------------"

pushd ./Server
python manage.py migrate
popd

echo "---------------------------------------"
echo "      DEPLOYING CENTRAL CONTROL        "
echo "---------------------------------------"

sed -i "s/{{ BUILD_NUMBER }}/${BUILD_NUMBER}/g" ./JenkinsScripts/deploy.yml
sed -i "s/{{ POSTGRES_URL }}/${POSTGRES_URL}/g" ./JenkinsScripts/deploy.yml
sed -i "s/{{ REDIS_URL }}/${REDIS_URL}/g" ./JenkinsScripts/deploy.yml
kubectl apply -f ./JenkinsScripts/deploy.yml
kubectl -n tactics rollout status deploy/tactics
