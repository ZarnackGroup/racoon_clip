#!/bin/bash

# Script to generate DAG with specific config file

CONFIG_FILE="/home/mek24iv/racoon_devel/racoon_clip/example_data/example_iCLIP_multiplexed/config_test_iCLIP_multiplexed.yaml"
OUTPUT_FILE="out_iCLIP_multiplexed/workflow_dag.txt"

echo "Generating DAG with config file: $CONFIG_FILE"
python ./generate_dag.py "$CONFIG_FILE" "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "DAG generation completed successfully!"
    echo "Output saved to: $OUTPUT_FILE"
else
    echo "DAG generation failed!"
    exit 1
fi
