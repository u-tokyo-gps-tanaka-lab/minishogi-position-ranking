#!/bin/bash

for f in x*;
do
    python check_reach.py $f 2>&1 > logs/$f &
done