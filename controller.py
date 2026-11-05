import argparse
import json
import paho.mqtt.client as mqtt

# Beispielgrenzen für die simulierte Maschine.
SWITCH_ON_C = 28.0
SWITCH_OFF_C = 26.0
COOLING_POWER_W = 100.0

requested_cooling = 0.0


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print("Verbindung abgelehnt:", reason_code)
        client.disconnect()
        return

    client.subscribe("industrial/production/status")
    client.subscribe("industrial/cooling/status")
    print("Controller verbunden; Statusmeldungen abonniert.")

def on_message(client, userdata, message):
    global requested_cooling

    data = json.loads(message.payload.decode())

    if message.topic == "industrial/production/status":
        # Alte Statusmeldungen enthalten noch keine Temperatur.
        if "temperature_c" not in data:
            return

        temperature = data["temperature_c"]

        if temperature >= SWITCH_ON_C:
            requested_cooling = COOLING_POWER_W
        elif temperature <= SWITCH_OFF_C:
            requested_cooling = 0.0

        client.publish(
            "industrial/cooling/request",
            json.dumps({
                "requested_cooling_w": requested_cooling,
            }),
        )

        print(
            f"Temperatur: {temperature:.3f} °C | "
            f"Kühlanforderung: {requested_cooling:.0f} W",
            flush=True,
        )

    elif message.topic == "industrial/cooling/status":
        if "delivered_cooling_w" not in data:
            return

        delivered_cooling = data["delivered_cooling_w"]

        client.publish(
            "industrial/production/cooling",
            json.dumps({
                "delivered_cooling_w": delivered_cooling,
            }),
        )

        print(
            f"Gelieferte Kühlung: {delivered_cooling:.2f} W "
            "→ Fertigung",
            flush=True,
        )


parser = argparse.ArgumentParser(
    description="Controller für Fertigung und Kühlung."
)
parser.add_argument("--broker", required=True, help="IP-Adresse des Brokers")
args = parser.parse_args()

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="fedora-controller",
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(args.broker, port=1883, keepalive=30)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nController beendet.")
finally:
    client.disconnect()
