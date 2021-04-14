#!/bin/bash

python3 classification_training.py \
    --rnn lstm \
    --epochs 10 \
    --split 0.8,0.1,0.1 \
    --num_trials 10

