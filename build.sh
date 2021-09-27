#!/bin/bash

# cd to the script directory https://stackoverflow.com/a/16349776/16790469
# why is bash the way it is
CURRENT_DIR=$(pwd)

cd "${0%/*}"

mkdir lambda-build
rm -rf lambda-build/*
cp -R src/lambda/*.py lambda-build/
pip install -r src/lambda/requirements.txt --target lambda-build/
cd lambda-build
zip -r -D lambda-code.zip ./*
cd -
mv lambda-build/lambda-code.zip .
rm -rf lambda-build

cd $CURRENT_DIR