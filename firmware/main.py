import network
import time
from umqtt.simple import MQTTClient

from config import CLIENT_ID, STATUS_TOPIC
from secrets import WIFI_SSID, WIFI_PASSWORD, MQTT_BROKER


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
client.connect()
print("MQTT verbunden:", CLIENT_ID)

counter = 0

while True:
    counter += 1
    payload = "online {}".format(counter)
    client.publish(STATUS_TOPIC, payload.encode())
    print(STATUS_TOPIC, payload)
    time.sleep(5)
