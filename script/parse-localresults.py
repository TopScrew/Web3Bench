# -*- coding: utf-8 -*-
import pandas as pd
import os
import csv
import math
import json
import xml.etree.ElementTree as ET

#________________________________________modify section_______________________________________________
# data = "test"
data = ""
#________________________________________modify section_______________________________________________

# The output CSV file name
export_csv_file = data + "res.csv"

# The test time in minutes, used to calculate the QPS and TPS
# # Get the test time from the shell
# print("Please enter the test time in minutes:")
# test_time = int(input())
# print(f"Test time: {test_time} minutes")
# Get the test time from the xml config file
xml_config_file = "../config/runthread1.xml"
tree = ET.parse(xml_config_file)
test_time = int(tree.find(".//time").text)
print(f"Get the test time from the xml config file {xml_config_file}")
print(f"Test time: {test_time} minutes")

# The latency limit of each transaction type
# The key is the transaction type name, and the value is the latency limit in seconds
latency_limit_file = open("latency-limit.json", "r")
latency_limit = json.load(latency_limit_file)

load_stats = {}

if data != "":
    data = data + "/"

csv_directory = "../results/" + data
print("Results directory: " + csv_directory)
print("Parsing results...")
for file in os.listdir("../results/" + data):
    if file.endswith(".csv"):
        file = os.path.join(csv_directory, file)
        df = pd.read_csv(file)
        for index, row in df.iterrows():
            type_name = row["Transaction Name"]
            l_time = row["Latency (microseconds)"]
            if type_name not in load_stats:
                load_stats[type_name] = {"Total Latency": 0, "Number of Requests": 0, "Latencies": []}
            load_stats[type_name]["Total Latency"] += l_time
            load_stats[type_name]["Number of Requests"] += 1
            load_stats[type_name]["Latencies"].append(l_time)

# Open the CSV file and write the header
with open(export_csv_file, mode="w", newline="") as file:
    fieldnames = [
        "Type Name", 
        "Total Latency(s)", 
        "Number of Requests", 
        "QPS", 
        "TPS", 
        "P99 Latency(s)", 
        "Geometric Mean Latency(s)", 
        "Avg Latency(s)", 
        "Avg Latency Limit", 
        "Pass/Fail"
    ]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for type_name, latency_limit in latency_limit.items():
        stats = load_stats.get(type_name)
        if stats:
            total_time = stats["Total Latency"] / 1000000 # Convert microseconds to seconds
            num = stats["Number of Requests"]
            latencies = stats["Latencies"]
            avg_time_s = total_time / num if num != 0 else 0
            qps = num / (test_time * 60)        # Queries per second
            tps = qps
            p99_latency = sorted(latencies)[int(0.99 * len(latencies))] / 1000000 # 99th percentile latency
            geometric_mean = math.exp(sum(math.log(lat) for lat in latencies) / len(latencies)) / 1000000 # Geometric mean of latencies
            writer.writerow({
                "Type Name": type_name,
                "Total Latency(s)": total_time,
                "Number of Requests": num,
                "QPS": qps,
                "TPS": tps,
                "P99 Latency(s)": p99_latency,
                "Geometric Mean Latency(s)": geometric_mean,
                "Avg Latency(s)": avg_time_s,
                "Avg Latency Limit": "N/A" if latency_limit == 0 else f"<={latency_limit}s",
                "Pass/Fail": "N/A" if latency_limit == 0 else "Pass" if avg_time_s <= latency_limit else "Fail"
            })

# Calculate the total statistics
total_total_latency = sum(stats["Total Latency"] for stats in load_stats.values()) / 1000000 # Convert microseconds to seconds
total_num_requests = sum(stats["Number of Requests"] for stats in load_stats.values())
total_latencies = [lat for stats in load_stats.values() for lat in stats["Latencies"]]
total_avg_time_s = total_total_latency / total_num_requests if total_num_requests != 0 else 0
total_qps = total_num_requests / (test_time * 60)        # Queries per second
total_tps = total_qps
total_p99_latency = sorted(total_latencies)[int(0.99 * len(total_latencies))] / 1000000
total_geometric_mean = math.exp(sum(math.log(lat) for lat in total_latencies) / len(total_latencies)) / 1000000

# Append the total data to the CSV file
with open(export_csv_file, mode="a", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writerow({
        "Type Name": "Total",
        "Total Latency(s)": total_total_latency,
        "Number of Requests": total_num_requests,
        "QPS": total_qps,
        "TPS": total_tps,
        "P99 Latency(s)": total_p99_latency,
        "Geometric Mean Latency(s)": total_geometric_mean,
        "Avg Latency(s)": total_avg_time_s,
        "Avg Latency Limit": "N/A",
        "Pass/Fail": "N/A"
    })

print(f"Data has been exported to '{export_csv_file}'")
