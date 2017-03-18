#! /bin/sh

# This link changes from time to time. I haven't found a reliable hosted installer package for doing regular
# installs like this. You will probably need to grab a current link from: http://unity3d.com/get-unity/download/archive
echo 'Downloading Pre-reqs: '
pip install -r ./Server/requirements.txt

# Create the database if it does not already exist
sudo ./Database/Create.sh tactics 12345

# Create the database tables for above database
python ./Server/manage.py makemigrations
python ./Server/manage.py migrate

npm install unity-solution-2 -g
unitysolution ./ Standalone