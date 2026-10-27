# MQTT-Kommunikation

[Zur Übersicht](../README.md) · [Einrichtung](01_setup.md)

## Prinzip und Gerätekennungen

Die Boards veröffentlichen Nachrichten bei Mosquitto. Der Broker leitet sie an Clients weiter, die das passende Topic abonniert haben. Im bisherigen Test übernimmt `mosquitto_sub` den Empfang auf Fedora.

| Board | Client-ID | Status-Topic |
|---|---|---|
| Fertigung | `esp32-production` | `industrial/production/status` |
| Kühlung | `esp32-cooling` | `industrial/cooling/status` |

Die **Client-ID** kennzeichnet die MQTT-Verbindung. Das **Topic** bestimmt die Zuordnung der Nachricht. Beide Boards verwenden unterschiedliche Client-IDs.

Voraussetzung: Die [Einrichtung](01_setup.md) ist abgeschlossen; beide Boards sind mit dem WLAN verbunden und der Broker ist erreichbar.

## 1. Empfang auf Fedora starten

In einem eigenen Fedora-Terminal ausführen und geöffnet lassen:

```bash
mosquitto_sub -h 192.168.178.28 -t 'industrial/+/status' -v
```

`+` ersetzt genau eine Topic-Ebene. Der Filter empfängt somit die Statusmeldungen von Fertigung und Kühlung. `-v` zeigt Topic und Nachrichteninhalt an.

## 2. Fertigungsboard senden lassen

In der MicroPython-Konsole des Fertigungsboards bei `>>>` ausführen:

```python
from umqtt.simple import MQTTClient

client = MQTTClient(
    client_id="esp32-production",
    server="192.168.178.28",
    port=1883,
)
client.connect()
client.publish(
    b"industrial/production/status",
    b"Hello from ESP32-S3 Production!",
)
client.disconnect()
```

## 3. Kühlungsboard senden lassen

In der MicroPython-Konsole des Kühlungsboards ausführen:

```python
from umqtt.simple import MQTTClient

client = MQTTClient(
    client_id="esp32-cooling",
    server="192.168.178.28",
    port=1883,
)
client.connect()
client.publish(
    b"industrial/cooling/status",
    b"Hello from ESP32-S3 Cooling!",
)
client.disconnect()
```

## Testergebnis

Auf Fedora wurden beide Nachrichten empfangen; die Reihenfolge hängt vom Sendezeitpunkt ab:

```text
industrial/cooling/status Hello from ESP32-S3 Cooling!
industrial/production/status Hello from ESP32-S3 Production!
```

Damit ist der einzelne Nachrichtenaustausch beider Boards über den Broker zum Abonnenten bestätigt. Jeder Aufruf verbindet sich, sendet einmal und trennt die Verbindung. Dauerhafter gleichzeitiger Betrieb, Wiederverbindung nach Ausfällen und automatischer Programmstart wurden damit noch nicht geprüft.

Bei Problemen: [Fehlersuche](troubleshooting.md).
