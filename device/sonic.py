import json
import os
import socket
import time

import RPi.GPIO as GPIO


HOST = os.getenv("NCUBE_TAS_HOST", "127.0.0.1")
PORT = int(os.getenv("NCUBE_TAS_PORT", "3105"))
CONTAINER = os.getenv("NCUBE_CONTAINER", "sonic")
TRIG = int(os.getenv("ULTRASONIC_TRIG_BCM", "23"))
ECHO = int(os.getenv("ULTRASONIC_ECHO_BCM", "24"))
ECHO_TIMEOUT_SECONDS = float(os.getenv("ULTRASONIC_ECHO_TIMEOUT", "0.05"))


def connect_to_tas():
    upload = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    upload.settimeout(5)
    upload.connect((HOST, PORT))
    upload.settimeout(None)
    return upload


def send_cin(upload, container, content):
    message = {"ctname": container, "con": content}
    payload = json.dumps(message) + "<EOF>"
    upload.sendall(payload.encode("utf-8"))


def wait_for_level(level, timeout_seconds):
    deadline = time.monotonic() + timeout_seconds
    while GPIO.input(ECHO) != level:
        if time.monotonic() >= deadline:
            return None
    return time.monotonic()


def measure_distance_cm():
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    pulse_start = wait_for_level(GPIO.HIGH, ECHO_TIMEOUT_SECONDS)
    if pulse_start is None:
        return None

    pulse_end = wait_for_level(GPIO.LOW, ECHO_TIMEOUT_SECONDS)
    if pulse_end is None:
        return None

    return (pulse_end - pulse_start) * 34300 / 2


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ECHO, GPIO.IN)

upload = None

try:
    print(f"Connecting to nCube TAS at {HOST}:{PORT}...")
    upload = connect_to_tas()
    print("Connected. Starting ultrasonic measurements.")
    time.sleep(2)

    while True:
        distance = measure_distance_cm()
        if distance is None:
            print("No echo received. Check the sensor wiring and target.")
        else:
            value = f"{distance:.1f}"
            send_cin(upload, CONTAINER, value)
            print(f"Distance: {value} cm")
        time.sleep(0.4)

except KeyboardInterrupt:
    print("Distance measurement stopped.")
except (ConnectionError, OSError) as error:
    print(f"TAS connection error: {error}")
    print("Start nCube with 'node thyme.js' before running sonic.py.")
finally:
    if upload is not None:
        upload.close()
    GPIO.cleanup()