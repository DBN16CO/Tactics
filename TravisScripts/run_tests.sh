#! /bin/sh

pushd ./Server/
coverage run manage.py test
popd