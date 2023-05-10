#!/bin/bash

# Define host info as a multiline string
host_info=$(cat "host_info.txt")

# Create logs directory if it does not exist
mkdir -p logs
rm -f logs/*

# Iterate through host_info and extract hostname, IP, and PID
while read -r line; do
  host_name=$(echo "$line" | awk -F':| ' '{print $2}')
  eth_ip=$(echo "$line" | awk -F':| ' '{print $5}')
  pid=$(echo "$line" | awk -F'pid=|>' '{print $2}')

  # Ping all other hosts
  # for target_line in $host_info; do
  while read -r target_line; do
    target_ip=$(echo "$target_line" | awk -F':| ' '{print $5}')
    if [[ "$eth_ip" != "$target_ip" ]]; then
      nohup mnexec -a $pid ping -i 1 -c 5 $target_ip >> "logs/ping_${host_name}.log" 2>&1 &
    fi
  done <<< "$host_info"
done <<< "$host_info"
