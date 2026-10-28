import json
import sys


DEVICES = {
    "industrial/production/status": "esp32-production",
    "industrial/cooling/status": "esp32-cooling",
}

for line in sys.stdin:
    try:
        topic, payload = line.strip().split(" ", 1)

        if topic not in DEVICES:
            raise ValueError("Unbekanntes Topic")

        message = json.loads(payload)

        if not isinstance(message, dict):
            raise ValueError("JSON-Objekt erwartet")

        if message.get("device_id") != DEVICES[topic]:
            raise ValueError("Gerätekennung passt nicht zum Topic")

        session = message.get("session_id")
        if (
            not isinstance(session, str)
            or len(session) != 16
            or any(c not in "0123456789abcdef" for c in session)
        ):
            raise ValueError("Ungültige Sitzungskennung")

        sequence = message.get("seq")
        if type(sequence) is not int or sequence < 1:
            raise ValueError("Sequenznummer muss eine positive Ganzzahl sein")

        if message.get("status") != "online":
            raise ValueError("Ungültiger Status")

        print(
            f"OK {message['device_id']} "
            f"Sitzung={session} seq={sequence}",
            flush=True,
        )

    except ValueError as error:
        print(f"UNGÜLTIG: {error}", flush=True)
