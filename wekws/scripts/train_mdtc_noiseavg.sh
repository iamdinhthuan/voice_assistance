#!/usr/bin/env bash
set -euo pipefail

# MDTC training + averaging + test (noise augment OFF; noise merged into negative).

CONFIG=conf/wake_mdtc.yaml
MODEL_DIR=exp/wake_mdtc_noaug_avg
NUM_AVG=10
GPUS=0

PYTHONPATH=. python -m wekws.bin.train \
  --gpus ${GPUS} \
  --config ${CONFIG} \
  --train_data data/train/data.list \
  --cv_data data/dev/data.list \
  --model_dir ${MODEL_DIR} \
  --num_workers 14 \
  --num_keywords 1 \
  --min_duration 50 \
  --seed 666 \
  --dict ./dict \
  --cmvn_file data/train/global_cmvn --norm_var \
  --prefetch 10

PYTHONPATH=. python -m wekws.bin.average_model \
  --dst_model ${MODEL_DIR}/avg_${NUM_AVG}.pt \
  --src_path ${MODEL_DIR} \
  --num ${NUM_AVG}

PYTHONPATH=. python -m wekws.bin.score \
  --config ${MODEL_DIR}/config.yaml \
  --test_data data/test/data.list \
  --dict ./dict \
  --gpu -1 \
  --checkpoint ${MODEL_DIR}/avg_${NUM_AVG}.pt \
  --batch_size 32 \
  --num_workers 14 \
  --prefetch 10 \
  --score_file ${MODEL_DIR}/test_score_avg${NUM_AVG}.txt

PYTHONPATH=. python -m wekws.bin.compute_det \
  --keyword "<WAKE>" \
  --test_data data/test/data.list \
  --window_shift 50 \
  --score_file ${MODEL_DIR}/test_score_avg${NUM_AVG}.txt \
  --stats_file ${MODEL_DIR}/test_stats_avg${NUM_AVG}.WAKE.txt
