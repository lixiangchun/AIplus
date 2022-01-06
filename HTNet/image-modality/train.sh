#!/bin/bash

export OMP_NUM_THREADS=1

python train.py \
--train-file train.csv \
--val-file valid.csv -b 8 \
--lr 0.001 --wd 1.0e-4 --lr-step-size 30 --epochs 80 \
-j 4 --output-dir ./ 


