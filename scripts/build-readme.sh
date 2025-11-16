#!/bin/bash
set -e

yaptex docs/main.md --target md --output readme-build
cp readme-build/md/index.md README.md
