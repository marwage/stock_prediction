#!/bin/bash

python3 training_blocks.py \
    --epochs 5 \
    --split 0.8,0.1,0.1 \
    --num_trials 20 \
    --loss mse
