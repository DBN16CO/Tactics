#! /bin/sh

# Change this the name of your project. This will be the name of the final executables as well.
project="Tactics"

echo "Attempting to build $project for Android"
/Applications/Unity/Unity.app/Contents/MacOS/Unity \
  -batchmode \
  -nographics \
  -silent-crashes \
  -logFile $(pwd)/unity.log \
  -projectPath $(pwd) \
  -executeMethod "AutoBuilder.PerformAndroidBuild" \
  -quit

rc=$?
if [ "$rc" -eq "1" ]; then
	echo 'Logs from build'
	cat $(pwd)/unity.log
	exit $rc
fi

echo 'Logs from build'
cat $(pwd)/unity.log

exit $rc