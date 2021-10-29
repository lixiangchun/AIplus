#!/bin/bash

export OMP_NUM_THREADS=1

python train.py \
--train-file hashimoto_thyroiditis_train.csv \
--val-file hashimoto_thyroiditis_valid.csv -b 16 \
--lr 0.0001 --wd 1.0e-5 --lr-step-size 30 --epochs 80 \
-j 4 --output-dir ./ 


