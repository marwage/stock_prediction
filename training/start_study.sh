#!/bin/bash

python3 training.py \
    --rnn lstm \
    --loss mse \
    --epochs 10 \
    --split 0.8,0.1,0.1 \
    --num_trials 50

