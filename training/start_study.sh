#!/bin/bash

python3 training.py \
    --loss mse \
    --epochs 10 \
    --split 0.8,0.1,0.1 \
    --num_trials 25 \
    --nonzero
    # --rnn lstm
