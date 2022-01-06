#!/bin/bash

export OMP_NUM_THREADS=1

python train.py \
--train-file train.csv \
--val-file valid.csv -b 2 --device cpu \
--antibodytrn antibody/train.csv \
--antibodyval antibody/valid.csv \
--lr 0.0001 --wd 1.0e-4 --lr-step-size 30 --epochs 30 \
-j 4 --output-dir ./ 


