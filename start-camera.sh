#!/bin/bash

# Infinite loop to keep the camera running
while true; do
    libcamera-hello
    sleep 1  # Optional: Add a small delay to prevent rapid restarts
done
