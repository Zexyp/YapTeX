#!/bin/bash
set -e

python -m unittest

shopt -s globstar
pylint yaptex
