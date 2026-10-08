#!/bin/bash

echo "Starting test of scheduled pipeline runs..."
echo "This will run the pipeline 5 times with 30-second intervals"

for i in {1..5}; do
    echo ""
    echo "=== Test Run $i/5 ==="
    echo "Starting at: $(date)"
    ./run_pipeline.sh
    echo "Completed at: $(date)"
    if [ $i -lt 5 ]; then
        echo "Waiting 30 seconds before next run..."
        sleep 30
    fi
done

echo ""
echo "=== Test Completed ==="
echo "Check logs/pipeline.log for detailed execution logs"
echo "Check reports/ directory for generated reports"
