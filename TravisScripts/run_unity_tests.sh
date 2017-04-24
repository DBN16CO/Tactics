#! /bin/bash

/opt/Unity/Editor/Unity -batchmode -logFile -projectPath ~/Documents/Tactics/ -runEditorTests -quit
result=$?
echo "The Unity tests ran with an error code of $result"
exit $result