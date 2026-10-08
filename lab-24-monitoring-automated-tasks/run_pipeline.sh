#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$" + "{BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')

echo "========================================" >> logs/pipeline.log
echo "Pipeline execution started at: $(date)" >> logs/pipeline.log
echo "========================================" >> logs/pipeline.log

python3 monitoring_pipeline.py
EXIT_CODE=$?

echo "========================================" >> logs/pipeline.log
echo "Pipeline execution ended at: $(date)" >> logs/pipeline.log
echo "Exit code: $EXIT_CODE" >> logs/pipeline.log
echo "========================================" >> logs/pipeline.log

exit $EXIT_CODE
