#!/bin/bash

for f in x*;
do
    python reach_partial.py $f 2> /dev/null &
done