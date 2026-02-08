#!/bin/bash

echo "Waiting for Redpanda to be ready..."
sleep 10

echo "Creating topics..."

# extract_daily_candidate 토픽 생성 (갭상승 종목 신호)
rpk topic create extract_daily_candidate \
  --brokers redpanda-0:9092 \
  --partitions 3 \
  --replicas 3

# 필요한 다른 토픽들을 여기에 추가
rpk topic create kis_websocket_commands \
  --brokers redpanda-0:9092 \
  --partitions 3 \
  --replicas 3

# model_retrain_command 토픽 생성 (재학습 트리거)
rpk topic create model_retrain_command \
  --brokers redpanda-0:9092 \
  --partitions 1 \
  --replicas 3

# model_retrain_result 토픽 생성 (재학습 결과)
rpk topic create model_retrain_result \
  --brokers redpanda-0:9092 \
  --partitions 1 \
  --replicas 3

# boliger_prediction_trigger 토픽 생성 (Boliger 모델 예측 트리거)
rpk topic create boliger_prediction_trigger \
  --brokers redpanda-0:9092 \
  --partitions 1 \
  --replicas 3

echo "Topics created successfully!"
echo "Current topics:"
rpk topic list --brokers redpanda-0:9092
