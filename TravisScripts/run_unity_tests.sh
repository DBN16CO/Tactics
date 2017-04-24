#! /bin/bash
/Applications/Unity/Unity.app/Contents/MacOS/Unity \
  -batchmode \
  -nographics \
  -silent-crashes \
  -logFile $(pwd)/unity_tests.log \
  -projectPath $(pwd) \
  -runEditorTests \
  -quit
result=$?
echo "The Unity tests ran with an error code of $result"
exit $result