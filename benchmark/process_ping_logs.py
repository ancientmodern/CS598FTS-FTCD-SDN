import os
import re
import csv
from collections import defaultdict

# Set the directory containing the log files
log_directory = "logs"

# Find all log files in the directory
log_files = [f for f in os.listdir(log_directory) if f.startswith("ping_")]

# Initialize a dictionary to store the latency times for each host
latency_data = defaultdict(lambda: defaultdict(lambda: "999"))

# Process each log file
for log_file in log_files:
    host_name = log_file.split(".")[0].split("_")[1]

    with open(os.path.join(log_directory, log_file), "r") as file:
        content = file.read()

        # Extract icmp_seq and latency times using a regular expression
        icmp_seq_latencies = re.findall(r"icmp_seq=(\d+).*time=([\d.]+)", content)

        # Store latency times with icmp_seq in the dictionary
        for icmp_seq, latency in icmp_seq_latencies:
            latency_data[host_name][int(icmp_seq)] = latency

# Sort the hosts based on switch order (s1h1, s1h2, ...)
sorted_hostnames = sorted(latency_data.keys(), key=lambda x: (x.split("s")[1], x.split("s")[0]))

# Get the sorted list of unique icmp_seq values
sorted_icmp_seq = sorted(set(seq for host in latency_data.values() for seq in host.keys()))

# Write the latency data to a CSV file
with open("benchmark/latency_data.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Write the header row
    writer.writerow(["icmp_seq"] + sorted_hostnames)

    # Write the icmp_seq and latency times
    for icmp_seq in sorted_icmp_seq:
        row = [icmp_seq] + [latency_data[hostname][icmp_seq] for hostname in sorted_hostnames]
        writer.writerow(row)
