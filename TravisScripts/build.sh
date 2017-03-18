# #! /bin/sh

xbuild /p:Configuration=Debug unity.sln
unitysolution ./ iOS && xbuild /p:Configuration=Debug unity.sln
unitysolution ./ Android && xbuild /p:Configuration=Debug unity.sln

# # Change this the name of your project. This will be the name of the final executables as well.
# project="Tactics"

# echo "Attempting to build $project for Windows"
# /Applications/Unity/Unity.app/Contents/MacOS/Unity \
#   -batchmode \
#   -nographics \
#   -silent-crashes \
#   -logFile $(pwd)/unity.log \
#   -projectPath $(pwd) \
#   -buildWindowsPlayer "$(pwd)/Build/windows/$project.exe" \
#   -quit

# rc=$?
# if [ "$rc" -eq "1" ]; then
# 	echo 'Logs from build'
# 	cat $(pwd)/unity.log
# 	exit $rc
# fi

# echo "Attempting to build $project for OS X"
# /Applications/Unity/Unity.app/Contents/MacOS/Unity \
#   -batchmode \
#   -nographics \
#   -silent-crashes \
#   -logFile $(pwd)/unity.log \
#   -projectPath $(pwd) \
#   -buildOSXUniversalPlayer "$(pwd)/Build/osx/$project.app" \
#   -quit

# rc=$?
# if [ "$rc" -eq "1" ]; then
# 	echo 'Logs from build'
# 	cat $(pwd)/unity.log
# 	exit $rc
# fi

# echo "Attempting to build $project for Linux"
# /Applications/Unity/Unity.app/Contents/MacOS/Unity \
#   -batchmode \
#   -nographics \
#   -silent-crashes \
#   -logFile $(pwd)/unity.log \
#   -projectPath $(pwd) \
#   -buildLinuxUniversalPlayer "$(pwd)/Build/linux/$project.exe" \
#   -quit

# echo 'Logs from build'
# cat $(pwd)/unity.log

# rc=$?
# if [ "$rc" -eq "1" ]; then
# 	exit $rc
# fi