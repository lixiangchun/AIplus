#!/bin/bash

export OMP_NUM_THREADS=1

python train.py \
--train-file ../hashimoto_thyroiditis/hashimoto_thyroiditis_train.csv \
--val-file ../hashimoto_thyroiditis/hashimoto_thyroiditis_valid.csv -b 16 \
--antibodytrn laboratory_testing_train.csv \
--antibodyval laboratory_testing_valid.csv \
--lr 0.0001 --wd 1.0e-4 --lr-step-size 30 --epochs 30 \
-j 4 --output-dir ./ 


