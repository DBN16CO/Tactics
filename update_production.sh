#!/bin/bash

echo "Please cd to the base directory of the Tactics Project"
read -p "Are you there? (y/n): " in_base
if [ $in_base != "y" ]; then
	echo "Please cd to the basic directory then!"
	exit 1
fi

git checkout master
if [ "$?" != "0" ]; then
	echo "Failed checkout master branch"
	exit 1
fi

git pull origin master
if [ "$?" != "0" ]; then
	echo "Failed to update local master branch"
	exit 1
fi

heroku login
if [ "$?" != "0" ]; then
	echo "Failed to authenticate with Heroku"
	exit 1
fi

pushd ./Server

git archive --remote=git@bitbucket.org:akkowal2/tactics-production.git HEAD Procfile | tar -xO > Procfile
if [ "$?" != "0" ]; then
	echo "Failed to checkout production Procfile"
	exit 1
fi

git archive --remote=git@bitbucket.org:akkowal2/tactics-production.git HEAD runtime.txt | tar -xO > runtime.txt
if [ "$?" != "0" ]; then
	echo "Failed to checkout production runtime.txt"
	exit 1
fi

rm -f ./Server/settings.py
if [ "$?" != "0" ]; then
	echo "Failed to delete development settings.py temporarily"
	exit 1
fi

pushd ./Server

git archive --remote=git@bitbucket.org:akkowal2/tactics-production.git HEAD settings.py | tar -xO > settings.py
if [ "$?" != "0" ]; then
	echo "Failed to checkout production settings.py"
	exit 1
fi

popd
popd

sleep 5

git add -A
git commit -m "auto-production-commit"

git push heroku `git subtree split --prefix Server master`:master --force
if [ "$?" != "0" ]; then
	echo "Failed to push changes to production"
	exit 1
fi

git reset --hard HEAD^

heroku run 'bash -c "python manage.py migrate"'
if [ "$?" != "0" ]; then
	echo "Failed to migrate production database"
	exit 1
fi