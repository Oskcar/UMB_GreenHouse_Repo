import csv
import os
import random
import sys
from pathlib import Path
import urllib.parse
import urllib.request

UPDATE_URL = "https://api.thingspeak.com/update"

if sys.prefix == sys.base_prefix:
    raise SystemExit("Refusing to send: activate a Python virtual environment first.")

WRITE_KEY = os.environ.get("THINGSPEAK_WRITE_KEY")
if not WRITE_KEY:
    raise SystemExit("No ThingSpeak write key found. Set THINGSPEAK_WRITE_KEY in this PowerShell session.")

csv_path = Path(__file__).with_name("nodes.csv")
with csv_path.open(newline="", encoding="utf-8-sig") as f:
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

        request = urllib.request.Request(
            UPDATE_URL,
            data=urllib.parse.urlencode(params).encode("utf-8"),
            method="POST",
        )
        print("Sending node", row["node_id"], "->", temperature, "C,", humidity, "%")
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                answer = response.read().decode().strip()
        except Exception as error:
            print("  Network problem:", error)
            continue

        if answer == "0":
            print("  Rejected: wrong key, or less than 15 s since the last write")
        else:
            print("  Stored as entry", answer)