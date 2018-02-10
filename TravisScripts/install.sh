#! /bin/sh

# This link changes from time to time. I haven't found a reliable hosted installer package for doing regular
# installs like this. You will probably need to grab a current link from: http://unity3d.com/get-unity/download/archive
echo 'Downloading Pre-reqs: '
sudo easy_install pip
sudo virtualenv env
source ./env/bin/activate
pip install -r ./Server/requirements.txt

# Setup PSQL and REDIS
export PG_DATA=$(brew --prefix)/var/postgres
rm -rf $PG_DATA
initdb $PG_DATA -E utf8
pg_ctl -w start -l postgres.log --pgdata ${PG_DATA}
createuser -s postgres
brew update
brew install redis
brew services start redis
redis-server --daemonize yes

echo 'Downloading from http://netstorage.unity3d.com/unity/b7e030c65c9b/MacEditorInstaller/Unity-5.4.2f2.pkg: '
curl -o Unity.pkg http://netstorage.unity3d.com/unity/b7e030c65c9b/MacEditorInstaller/Unity-5.4.2f2.pkg

echo 'Installing Unity.pkg'
sudo installer -dumplog -package Unity.pkg -target /