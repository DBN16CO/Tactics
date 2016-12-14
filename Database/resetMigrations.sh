#!/bin/bash

# This file will remove all migrations for all apps
# and then remove the database and re-create it
# 
# This is useful to run when you need to update the models
# during database creation - should not be used when a
# production version exists

# First get the home directory
if [ $# -eq 0 ]
  then
    echo "Using default project home: ~/Documents/Tactics"
    home=~/Documents/Tactics
else
	home=$1
fi

# Hide output of pushd and popd
pushd () {
    command pushd "$@" > /dev/null
}

popd () {
    command popd "$@" > /dev/null
}

# Ensure that location is accurate
pushd ${home} || (echo "Invalid path"; exit)
popd

# Delete all files in the Communication app
echo "Communication:"
pushd ${home}/Server/Communication/migrations \
&& echo "Removing the following files:" \
&& ls | grep -v '__init__.py' \
&& ls | grep -v '__init__.py' | xargs rm &> ./null \
&& rm null \
&& popd

# Delete all files in the Game app
echo "Game:"
pushd ${home}/Server/Game/migrations \
&& echo "Removing the following files:" \
&& ls | grep -v '__init__.py' \
&& ls | grep -v '__init__.py' | xargs rm &> ./null \
&& rm null \
&& popd

# Delete all files in the Static app
echo "Static:"
pushd ${home}/Server/Static/migrations \
&& echo "Removing the following files:" \
&& ls | grep -v '__init__.py' \
&& ls | grep -v '__init__.py' | xargs rm &> ./null \
&& rm null \
&& popd

# Delete all files in the User app
echo "User:"
pushd ${home}/Server/User/migrations \
&& echo "Removing the following files:" \
&& ls | grep -v '__init__.py' \
&& ls | grep -v '__init__.py' | xargs rm &> ./null \
&& rm null \
popd

popd

# Drop and add the database
echo "DROP DATABASE tactics;" | sudo -u postgres psql 
echo "CREATE DATABASE tactics;" | sudo -u postgres psql 