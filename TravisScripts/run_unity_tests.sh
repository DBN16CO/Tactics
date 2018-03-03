#! /bin/bash
/Applications/Unity/Unity.app/Contents/MacOS/Unity \
  -batchmode \
  -nographics \
  -silent-crashes \
  -logFile $(pwd)/unity_logfile.log \
  -projectPath $(pwd) \
  -editorTestsResultFile $(pwd)/unity_tests.xml \
  -runEditorTests
result=$?
echo "The Unity tests ran with an exit code of $result"

echo "-------------START unity_tests.xml-------------"
cat $(pwd)/unity_tests.xml
echo "-------------END unity_tests.xml-------------"

echo "-------------START unity_logfile.log-------------"
#cat $(pwd)/unity_logfile.log
cat ~/Library/Logs/Unity/Editor.log
echo "-------------END unity_logfile.log-------------"

exit $result