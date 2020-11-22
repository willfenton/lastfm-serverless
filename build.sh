#!/bin/bash

rm -rf build/*
cp -R src/lambda/*.py build/
pip install -r src/lambda/requirements.txt --target build/
cd build
zip -r lambda-code.zip ./*
