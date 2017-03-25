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

echo y | android update sdk --no-ui --all --filter "android-25,build-tools-25.0.2platform-tools,extra-android-m2repository,extra-google-m2repository"

ls -al /usr/local/Cellar/android-sdk/
export ANDROID_SDK_ROOT=/usr/local/Cellar/android-sdk/24.4.1_1/

echo 'Downloading unity 5.5.0f3 binaries:'
curl -o Unity.pkg http://netstorage.unity3d.com/unity/38b4efef76f0/MacEditorInstaller/Unity-5.5.0f3.pkg
curl -o Unity-Android.pkg http://netstorage.unity3d.com/unity/38b4efef76f0/MacEditorTargetInstaller/UnitySetup-Android-Support-for-Editor-5.5.0f3.pkg

#echo 'Downloading from http://netstorage.unity3d.com/unity/b7e030c65c9b/MacEditorInstaller/Unity-5.4.2f2.pkg: '
#curl -o Unity.pkg http://netstorage.unity3d.com/unity/b7e030c65c9b/MacEditorInstaller/Unity-5.4.2f2.pkg

echo 'Installing Unity.pkg and Unity-Android.pkg'
sudo installer -dumplog -package Unity.pkg -target /

sudo installer -dumplog -package Unity-Android.pkg -target /