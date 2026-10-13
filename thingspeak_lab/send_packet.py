import csv
import os
import random
import urllib.parse
import urllib.request

UPDATE_URL = "https://api.thingspeak.com/update"
WRITE_KEY = os.environ.get("THINGSPEAK_WRITE_KEY")  # Replaced with Location Test Channel ThingSpeak Write API Key

#Eventually higher security will be needed, but for now, this is a simple test script to send data to ThingSpeak

#if not WRITE_KEY:
    #print("No Write key found. Set it with:")
    #print('  $env:THINGSPEAK_WRITE_KEY = "YOUR_KEY"')
    #raise SystemExit(1)

with open("nodes1.csv", newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["enabled"].strip().lower() != "yes":
            continue

        lat = float(row["lat"])
        lon = float(row["lon"])
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            print("Bad coordinates for", row["name"])
            continue

        # Fake sensor readings, until a real sensor exists
        temperature = round(random.uniform(18, 30), 1)
        humidity = round(random.uniform(40, 80), 1)

        params = {
            "api_key": WRITE_KEY,
            "field1": row["node_id"],
            "field2": temperature,
            "field3": humidity,
            "lat": lat,
            "long": lon,               # our "lon" becomes ThingSpeak's "long"
            "elevation": row["elevation_m"],
        }

        url = UPDATE_URL + "?" + urllib.parse.urlencode(params)
      #  print("Would send:", url.replace(str(WRITE_KEY), "HIDDEN"))    #Here we can test the URL without sending it

      #  # Send the request to ThingSpeak
      #  try:
        print("Sending node", row["node_id"], "->", temperature, "C,", humidity, "%")
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                answer = response.read().decode().strip()
        except Exception as error:
            print("  Network problem:", error)
            continue

        if answer == "0":
            print("  Rejected: wrong key, or less than 15 s since the last write")
        else:
            print("  Stored as entry", answer)