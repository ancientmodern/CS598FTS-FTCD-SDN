#!/bin/bash

pid=$1
eth_ip=$2

# Define host info as a multiline string
host_info=$(cat "host_info.txt")

# Create logs directory if it does not exist
mkdir -p logs
rm -f logs/*

# Iterate through host_info and extract hostname, IP, and PID
while read -r target_line; do
    host_name=$(echo "$target_line" | awk -F':| ' '{print $2}')
    target_ip=$(echo "$target_line" | awk -F':| ' '{print $5}')
    if [[ "$eth_ip" != "$target_ip" ]]; then
        nohup mnexec -a $pid ping -i 0.2 -c 300 $target_ip >> "logs/ping_${host_name}.log" 2>&1 &
    fi
done <<< "$host_info"
