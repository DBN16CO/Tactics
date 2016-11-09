#! /bin/bash

pushd ./Server/
coverage run manage.py test
popd