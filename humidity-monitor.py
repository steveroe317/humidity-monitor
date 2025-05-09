#!/usr/bin/env python3
"""Implements a simple humidity-monitor on a Raspberry Pi.

The monitor measures temperature and humidity using a DHT22 AM2303 sensor.

The thresholds, sampling period, and log file name are hard-coded.
"""

import adafruit_dht  # type: ignore
import board  # type: ignore
import datetime
import digitalio  # type: ignore
import firebase_admin  # type: ignore
import os
import time
import shutil
import sys

from firebase_admin import credentials
from firebase_admin import firestore


# Take a humidty and temperature measurement every 5 minutes.
# The sampling period must be long enough that a month's
# worth of firestore data us uner 1 megabyte.
sample_period_s = 300.0

# On-server log location and rotation specifications.
log_name = "/var/log/humidity-monitor/humidity.log"
log_size_limit = 1_000_000
log_rotate_count = 4

# Firestore service account key and document path.
app_service_key_path = os.getenv("APP_SERVICE_KEY")
app_site = os.getenv("APP_SITE", "test_site")
app_location = os.getenv("APP_LOCATION", "test_location")
app_location_month = ""

# Set up optional access to Google Firestore database.
if not app_service_key_path:
    firestore_db = None
else:
    cred = credentials.Certificate(app_service_key_path)
    app = firebase_admin.initialize_app(cred)
    firestore_db = firestore.client()
firestore_doc_ref = None

# Set up interface for temperature sensor.
dht_device = adafruit_dht.DHT22(board.D24)


def rotate_logs(log_name: str) -> None:
    """Rotates log files, keeps log_rotate_count-1 old logs."""

    log_names = [f"{log_name}.{index}" for index in range(log_rotate_count)]
    log_names[0] = log_name

    for index in reversed(range(log_rotate_count - 1)):
        if os.path.isfile(log_names[index]):
            shutil.move(log_names[index], log_names[index + 1])


while True:
    try:
        # Read temperature and humidity from the sensor.  The humidity value
        # is not used for heater control, but if it is None an error is assumed
        # to have occurred.
        temperature_c = dht_device.temperature
        if temperature_c is None:
            continue
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dht_device.humidity
        if humidity is None:
            continue

        temperature_c = round(temperature_c)
        temperature_f = round(temperature_f)
        humidity = round(humidity)

        # Rotate log files if needed.
        if os.path.isfile(log_name):
            if os.path.getsize(log_name) > log_size_limit:
                rotate_logs(log_name)

        # Log the current sensor readings and heater state.
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y/%m/%d %H:%M:%S")
        message = f"time:{timestamp},temp:{temperature_f},rh:{humidity}\n"
        print(message, end="")
        with open(log_name, "a") as f:
            f.write(message)

        # Optionally log data to the firestire database.
        if firestore_db is not None:
            # Use a separate document for each month to stay under firestore's
            # 1 megabyte document size limit.
            location_month = f'{app_location}-{now.strftime("%Y-%m")}'
            if app_location_month != location_month:
                app_location_month = location_month
                firestore_doc_ref = firestore_db.collection(app_site).document(
                    app_location_month
                )
            if firestore_doc_ref:
                data = {timestamp: {"t": temperature_f, "rh": humidity}}
                firestore_doc_ref.set(data, merge=True)

    except RuntimeError as err:
        print(err.args[0])

    # Wait N seconds before checking the temperature again.
    time.sleep(sample_period_s)

# If the loop terminates, exit with an error
sys.exit(1)
