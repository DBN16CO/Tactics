#! /bin/bash
pwd
/Applications/Unity/Unity.app/Contents/MacOS/Unity -batchmode -logFile -projectPath ./ -runEditorTests -quit
result=$?
echo "The Unity tests ran with an error code of $result"
exit $result