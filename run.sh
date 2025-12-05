#!/bin/bash
while true; do
    echo "Starting Mizu..."
    python mizu.py
    echo "Mizu stopped. Restarting in 5 seconds..."
    sleep 5
done
