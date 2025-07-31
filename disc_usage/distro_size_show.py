#!/bin/env python3

import csv
from datetime import datetime

LOG_FILE_PATH = "/var/log/distro_disk_usage.log"

with open(LOG_FILE_PATH, "r") as csv_file:
    # dialect = csv.Sniffer().sniff(csv_file.read())
    # csv_file.seek(0)
    csv_reader = csv.reader(csv_file)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            row[1] = "Size (GB)"
        else:
            row[0] = datetime.fromisoformat(row[0]).strftime("%d-%b-%y %H:%M")
            row[1] += '\t'
        row[0] += '\t'
        print("\t".join(row))
        line_count += 1
