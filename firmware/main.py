import network
import time
import json
import os
import binascii
from umqtt.simple import MQTTClient

from config import CLIENT_ID, STATUS_TOPIC, INPUT_TOPIC
from secrets import WIFI_SSID, WIFI_PASSWORD, MQTT_BROKER

# Modell und Anfangszustand dieses Boards.
if CLIENT_ID == "esp32-production":
    from thermal_model import update_temperature

    temperature = 25.0

elif CLIENT_ID == "esp32-cooling":
    from cooling_model import update_cooling

    delivered_cooling = 0.0

else:
    raise ValueError("Unbekannte Gerätekennung")

# Zuletzt empfangene Kühlleistung in Watt.
input_power = 0.0


def receive_message(topic, payload):
    global input_power

    message = json.loads(payload)

    if CLIENT_ID == "esp32-production":
        input_power = message["delivered_cooling_w"]
    else:
        input_power = message["requested_cooling_w"]

    print("Empfangene Kühlleistung:", input_power, "W")


wlan = network.WLAN(network.STA_IF)
wlan.active(True)

if not wlan.isconnected():
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

for _ in range(20):
    if wlan.isconnected():
        break
    time.sleep(1)

if not wlan.isconnected():
    raise RuntimeError("WLAN-Verbindung fehlgeschlagen")

print("WLAN verbunden:", wlan.ifconfig()[0])

client = MQTTClient(
    client_id=CLIENT_ID,
    server=MQTT_BROKER,
    port=1883,
    keepalive=30,
)

client.set_callback(receive_message)
client.connect()
client.subscribe(INPUT_TOPIC)

print("MQTT verbunden:", CLIENT_ID)
session_id = binascii.hexlify(os.urandom(8)).decode()
counter = 0

last_step = time.ticks_ms()

while True:
    # Eingehende Nachrichten verarbeiten und input_power aktualisieren.
    client.check_msg()

    now = time.ticks_ms()

    if time.ticks_diff(now, last_step) >= 1000:
        last_step = now
        counter += 1

        message = {
            "device_id": CLIENT_ID,
            "session_id": session_id,
            "seq": counter,
            "status": "online",
        }

        if CLIENT_ID == "esp32-production":
            temperature = update_temperature(
                temperature=temperature,
                ambient=20.0,
                heating_power=100.0,
                cooling_power=input_power,
                heat_capacity=1000.0,
                loss_coefficient=5.0,
                dt=1.0,
            )

            message["temperature_c"] = temperature
            message["applied_cooling_w"] = input_power

        else:
            delivered_cooling = update_cooling(
                delivered_power=delivered_cooling,
                requested_power=input_power,
                max_power=100.0,
                response_time=10.0,
                dt=1.0,
            )

            message["requested_cooling_w"] = input_power
            message["delivered_cooling_w"] = delivered_cooling

        payload = json.dumps(message)
        client.publish(STATUS_TOPIC, payload.encode())
        print(STATUS_TOPIC, payload)

    time.sleep_ms(20)
