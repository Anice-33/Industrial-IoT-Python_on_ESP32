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

Damit ist der manuelle Nachrichtenaustausch beider Boards bestätigt.
Der folgende Test erweitert diesen Nachweis um den automatischen Betrieb.

## Automatischer Sendebetrieb

Beide Boards verwenden dasselbe Programm
[firmware/main.py](../firmware/main.py).
Die gerätespezifischen Kennungen stehen in
[production/config.py](../firmware/production/config.py) und
[cooling/config.py](../firmware/cooling/config.py).

Auf jedem Board liegen im Hauptverzeichnis:

- `main.py`: WLAN-Verbindung, MQTT-Verbindung und Sendeschleife.
- `config.py`: Client-ID und Status-Topic des jeweiligen Boards.
- `secrets.py`: lokale WLAN-Zugangsdaten und Broker-Adresse;
  diese Datei wird nicht versioniert.

Nach dem Start wartet das Programm bis zu ungefähr 20 Sekunden auf die
WLAN-Verbindung. Sobald sie besteht, verbindet es sich mit MQTT und
veröffentlicht etwa alle fünf Sekunden `online <Zähler>`. Der Zähler
beginnt nach jedem Programmstart wieder bei 1.

### Prüfung am 28.10.2026

1. Den Terminal-Abonnenten auf Fedora starten.
2. Beide Boards über RESET/EN neu starten.
3. Prüfen, dass beide Topics wieder mit `online 1` beginnen.
4. Den gemeinsamen Sendebetrieb mindestens zwei Minuten beobachten.

| Prüfung | Beobachtung |
|---|---|
| Automatischer Start nach Reset | Beide Boards sendeten ab Zähler 1 |
| Beobachtungszeitraum | 08:03:56–08:06:16, insgesamt 2 min 20 s |
| Zählerstände | Beide Boards von 22 bis 50 |
| Empfangsabstand | Überwiegend fünf Sekunden; eine sichtbare Abweichung von ungefähr einer Sekunde |

Die Zeitstempel wurden beim Lesen der Nachrichten auf Fedora mit
Sekundenauflösung ergänzt. Sie zeigen die Empfangsfolge und sind
keine genaue Messung der Übertragungslatenz. Zähler 39 fehlt im
bereitgestellten Auszug; daraus lässt sich kein Nachrichtenverlust ableiten.

Der Test bestätigt den automatischen Start und den gemeinsamen
Sendebetrieb im beobachteten Zeitraum. Automatische Wiederverbindung
und Fehlerbehandlung bei Verbindungsabbrüchen sind noch nicht umgesetzt.

Bei Problemen: [Fehlersuche](troubleshooting.md).
