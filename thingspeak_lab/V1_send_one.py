
#Read the CSV file and print it [Version 1]
import csv

with open("nodes1.csv", newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)

