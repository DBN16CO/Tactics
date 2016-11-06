#! /bin/sh

# Change this the name of your project. This will be the name of the final executables as well.
#project="Tactics"

#Test that the Django server is up and running
curl -I http://localhost:8000

#echo "Attempting to build $project for Windows"
#/Applications/Unity/Unity.app/Contents/MacOS/Unity \
#  -batchmode \
#  -nographics \
#  -silent-crashes \
#  -logFile $(pwd)/unity.log \
#  -projectPath $(pwd) \
#  -buildWindowsPlayer "$(pwd)/Build/windows/$project.exe" \
#  -quit

#echo "Attempting to build $project for OS X"
#/Applications/Unity/Unity.app/Contents/MacOS/Unity \
#  -batchmode \
#  -nographics \
#  -silent-crashes \
#  -logFile $(pwd)/unity.log \
#  -projectPath $(pwd) \
#  -buildOSXUniversalPlayer "$(pwd)/Build/osx/$project.app" \
#  -quit

#echo "Attempting to build $project for Linux"
#/Applications/Unity/Unity.app/Contents/MacOS/Unity \
#  -batchmode \
#  -nographics \
#  -silent-crashes \
#  -logFile $(pwd)/unity.log \
#  -projectPath $(pwd) \
#  -buildLinuxUniversalPlayer "$(pwd)/Build/linux/$project.exe" \
#  -quit

#echo 'Logs from build'
#cat $(pwd)/unity.log