#!/bin/bash

for i in $(seq -f "%02g" 1 10)
do
    time ./testqlearner.py testworlds/world$i.csv -i 500 -m
    echo
done
