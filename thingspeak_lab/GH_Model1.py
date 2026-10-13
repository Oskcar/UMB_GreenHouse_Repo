
#Read the CSV file and print it [Version 1]
import csv  #Loads the CSV module

with open("nodes.csv", newline="", encoding="utf-8-sig") as f:  #opens/closes the CSV file when block ends (newline = "" to avoid blank lines, encoding = "utf-8-sig" to avoid BOM issues)  
    reader = csv.DictReader(f) #csv.DictReader uses the header row to create a dictionary for each subsequent row, with the header values as keys and the row values as values
    for row in reader:  #Repeats indented code once per row
        if row["enabled"].strip().lower() != "yes":  #Checks if the "enabled" column value is "yes" (case insensitive, with whitespace stripped)
            continue  #Skips the rest of the loop and goes to the next row if "enabled" is "yes"  

        lat = float(row["lat"])
        lon = float(row["lon"])

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):  #Checks if the latitude and longitude values are within valid ranges
            print(f"Invalid coordinates for node {row['node_id']}: lat={lat}, lon={lon}")  #Prints an error message if the coordinates are invalid
            continue
        print(row["node_id"], row["name"], lat, lon)    