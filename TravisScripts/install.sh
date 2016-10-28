#! /bin/sh

# This link changes from time to time. I haven't found a reliable hosted installer package for doing regular
# installs like this. You will probably need to grab a current link from: http://unity3d.com/get-unity/download/archive
echo 'Downloading Pre-reqs: '
pip install -r ./TacticsServer/requirements.txt

python ./TacticsServer/manage.py runserver
#echo 'Downloading from http://netstorage.unity3d.com/unity/b7e030c65c9b/MacEditorInstaller/Unity-5.4.2f2.pkg: '
#curl -o Unity.pkg http://netstorage.unity3d.com/unity/b7e030c65c9b/MacEditorInstaller/Unity-5.4.2f2.pkg

#echo 'Installing Unity.pkg'
#sudo installer -dumplog -package Unity.pkg -target /