#!/bin/sh

# This file will remove all migrations for all apps
# and then remove the database and re-create it
# 
# This is useful to run when you need to update the models
# during database creation - should not be used when a
# production version exists

# First get the home directory
if [ $# -eq 0 ]
  then
    echo "Plese supply the home directory of the tactics project (including the project)."
    echo "For example: ./resetMigrations.sh ~/Documents/Tactics"
    return
fi

home=$1

# Ensure that location is accurate
cd ${home} || (echo "Invalid path"; exit)

# Delete all files in the Communication app
echo "Communication:"
cd ${home}/Server/Communication/migrations \
&& echo "Removing the following files:" \
&& ls | grep -v '__init__.py' \
&& ls | grep -v '__init__.py' | xargs rm &> ./null || rm null

# Delete all files in the Game app
echo "Game:"
cd ${home}/Server/Game/migrations \
&& echo "Removing the following files:" \
&& ls | grep -v '__init__.py' \
&& ls | grep -v '__init__.py' | xargs rm &> ./null || rm null

# Delete all files in the Static app
echo "Static:"
cd ${home}/Server/Static/migrations \
&& echo "Removing the following files:" \
&& ls | grep -v '__init__.py' \
&& ls | grep -v '__init__.py' | xargs rm &> ./null || rm null

# Delete all files in the User app
echo "User:"
cd ${home}/Server/User/migrations \
&& echo "Removing the following files:" \
&& ls | grep -v '__init__.py' \
&& ls | grep -v '__init__.py' | xargs rm &> ./null || rm null

cd ${home}

# Drop and add the database
echo "DROP DATABASE tactics;" | sudo -u postgres psql 
echo "CREATE DATABASE tactics;" | sudo -u postgres psql 