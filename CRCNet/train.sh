#!/bin/bash

python train.py --train-file trn.csv --val-file val.csv -b 32 --num-classes 2 --pretrained

