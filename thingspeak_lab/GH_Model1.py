
#Read the CSV file, print it, build the request without sending it [Version 3]
import csv  
import os  
import random  
import urllib.parse

#ThingSpeak Section
UPDATE_URL = "https://api.thingspeak.com/update"  #ThingSpeak API URL for updating channel data
WRITE_KEY = os.environ.get("THINGSPEAK_WRITE_KEY")  #Get the ThingSpeak Write API Key from the environment variable "THINGSPEAK_WRITE_KEY"

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

# Fake sensor readings, until a real sensor exists

        temperature = round(random.uniform(18, 30), 1)  #Generates a random temperature value between 18 and 30 degrees Celsius, rounded to one decimal place
        humidity = round(random.uniform(40, 80), 1)  #Generates a random humidity value between 40% and 80%, rounded to one decimal place

        params = {  #Creates a dictionary of parameters to send to ThingSpeak
            "api_key": WRITE_KEY,
            "field1": row["node_id"],
            "field2": temperature,
            "field3": humidity,
            "lat": lat,
            "long": lon,               # our "lon" becomes ThingSpeak's "long"
            "elevation": row["elevation_m"],
        }

        url = UPDATE_URL + "?" + urllib.parse.urlencode(params)  #Builds the full URL for the request by appending the encoded parameters to the base URL
        print("Would send:", url.replace(str(WRITE_KEY), "HIDDEN"))    #Prints the URL with the API key hidden for testing purposes   