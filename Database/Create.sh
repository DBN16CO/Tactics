#!/bin/sh

# This script is used to create the database

# Get the input argument for the database name
if [ $# -eq 0 ]
  then
 	echo "This script will setup your postgres database."
 	echo "It assumes you already have postgres, if not:"
 	echo "For mac use: brew install postgres"
 	echo "For linux use: sudo apt-get install postgresql"
 	echo "For windows use: get on mac or linux"
    echo "This script takes two inputs,"
    echo "the first being the datbase name,"
    echo "and the second being the password for the default user 'postgres'."
    echo "For example:"
    echo "./Create.sh tblname 12345"
    echo "If no second input is provided, the password 12345 is used."
    exit
else
	dbname=$1
fi

# Create the database
sql="CREATE DATABASE $dbname;"

# Get the input argument for the password
if [ $# -eq 0 ]
  then
    password="12345"
else
	password=$2
fi

# Set the password for the database, using 12345
sql=$sql"ALTER ROLE postgres WITH PASSWORD '$password';"

# Log into the database and run all of the commands
echo $sql | sudo postgres psql