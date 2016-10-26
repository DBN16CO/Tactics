#! /bin/sh

# This link changes from time to time. I haven't found a reliable hosted installer package for doing regular
# installs like this. You will probably need to grab a current link from: http://unity3d.com/get-unity/download/archive
echo 'Downloading Apache Tomcat 8: '
curl -o apache-tomcat-8.5.6.tar.gz http://www-us.apache.org/dist/tomcat/tomcat-8/v8.5.6/bin/apache-tomcat-8.5.6.tar.gz

echo 'Untaring Apache Tomcat 8: '
tar -zxvf apache-tomcat-8.5.6.tar.gz

pushd apache-tomcat-8.5.6/bin
./startup.sh &disown
popd

echo 'Downloading from http://netstorage.unity3d.com/unity/b7e030c65c9b/MacEditorInstaller/Unity-5.4.2f2.pkg: '
curl -o Unity.pkg http://netstorage.unity3d.com/unity/b7e030c65c9b/MacEditorInstaller/Unity-5.4.2f2.pkg

echo 'Installing Unity.pkg'
sudo installer -dumplog -package Unity.pkg -target /