
import csv
import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


UPDATE_URL = "https://api.thingspeak.com/update"
CSV_FILE = "nodes.csv"
GAP_SECONDS = 16   # free tier: max one write every 15 s per channel


def load_nodes(path):
    """Return the enabled nodes from the CSV, with numbers already converted."""
    nodes = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["enabled"].strip().lower() != "yes":
                continue
            lat = float(row["lat"])
            lon = float(row["lon"])
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                print("Bad coordinates for", row["name"], "- skipped")
                continue
            nodes.append({
                "node_id": row["node_id"],
                "name": row["name"],
                "lat": lat,
                "lon": lon,
                "elevation": row["elevation_m"],
            })
    return nodes


def read_sensors(node):
    """Fake readings for now. On a Raspberry Pi, only this function changes."""
    return {
        "temperature": round(random.uniform(18, 30), 1),
        "humidity": round(random.uniform(40, 80), 1),
    }


def send_reading(write_key, node, reading):
    """Send one row to ThingSpeak. Return (success, message)."""
    params = {
        "api_key": write_key,
        "field1": node["node_id"],
        "field2": reading["temperature"],
        "field3": reading["humidity"],
        "lat": node["lat"],
        "long": node["lon"],
        "elevation": node["elevation"],
    }
    url = UPDATE_URL + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            answer = response.read().decode().strip()
    except urllib.error.HTTPError as error:
        return False, f"refused: HTTP {error.code} {error.reason}"
    except urllib.error.URLError as error:
        return False, f"network problem: {error.reason}"

    if answer == "0":
        return False, "rejected (too fast, or bad key)"
    return True, f"stored as entry {answer}"


def load_env_file(path=".env"):
    """Load KEY=VALUE pairs from a .env file without overriding the environment."""
    env_path = Path(path)
    if not env_path.is_file():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or not key or key in os.environ:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ[key] = value


def main():
    load_env_file()
    write_key = os.environ.get("THINGSPEAK_WRITE_KEY")
    if not write_key:
        print("No Write key found. Add it to your .env file.")
        return

    stored = 0
    failed = 0
    round_number = 0
    print("Running. Press Ctrl+C to stop.")

    try:
        while True:
            round_number += 1
            try:
                nodes = load_nodes(CSV_FILE)
            except (OSError, ValueError, KeyError) as error:
                print(f"Could not read {CSV_FILE}: {error}. Trying again soon.")
                time.sleep(GAP_SECONDS)
                continue

            if not nodes:
                print("No enabled nodes. Checking again soon.")
                time.sleep(GAP_SECONDS)
                continue

            print(f"--- Round {round_number}: {len(nodes)} node(s) ---")
            for node in nodes:
                reading = read_sensors(node)
                ok, message = send_reading(write_key, node, reading)
                stamp = time.strftime("%H:%M:%S")
                print(f"{stamp}  node {node['node_id']}  "
                      f"{reading['temperature']} C  {reading['humidity']} %  -> {message}")
                if ok:
                    stored += 1
                else:
                    failed += 1
                time.sleep(GAP_SECONDS)
    except KeyboardInterrupt:
        print(f"\nStopped after {round_number} round(s): {stored} stored, {failed} failed.")


if __name__ == "__main__":
    main()

    