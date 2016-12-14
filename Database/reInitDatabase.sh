#!/bin/bash

# This file will remove all migrations for all apps
# and then remove the database and re-create it
# further, it will rerun the makemigrations, migrate, and init the DB
# 
# This is useful to run when you need to update the models
# during database creation - should not be used when a
# production version exists

# First reset the migrations and recreate the DB
. ~/Documents/Tactics/Database/resetMigrations.sh

# Next recreate the migrations
pushd ${home}/Server && python manage.py makemigrations || (echo "Error during makemigrations" && exit 0)
python manage.py migrate || (echo "Error during migrate" && popd && exit 0)

# Ask user for versions to initialize
echo "Input comma-separated versions to initialize, then press [ENTER]:"
read versions
python manage.py db_init $versions
popd