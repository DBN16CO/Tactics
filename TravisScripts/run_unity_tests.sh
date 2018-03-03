#! /bin/bash
/Applications/Unity/Unity.app/Contents/MacOS/Unity \
  -batchmode \
  -nographics \
  -silent-crashes \
  -logFile $(pwd)/unity_logfile.log \
  -projectPath $(pwd) \
  -editorTestsResultFile /tmp/unity_tests.xml \
  -runEditorTests \
  -quit
result=$?
echo "The Unity tests ran with an exit code of $result"

#echo "-------------START unity_logfile.log-------------"
#cat $(pwd)/unity_logfile.log
#echo "-------------END unity_logfile.log-------------"

echo "-------------START unity_tests.log-------------"
cat /tmp/unity_tests.xml
echo "-------------END unity_tests.log-------------"

exit $result