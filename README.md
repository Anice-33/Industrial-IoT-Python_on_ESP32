# Industrial IoT: Vernetzte Fertigung und Kühlung

## Projektziel

Zwei ESP32-S3 sollen eine Fertigungsmaschine und eine Kühleinheit simulieren. Eine Python-Anwendung auf Linux soll ihre Zustände überwachen und die Kühlung steuern. Das Projekt untersucht das Verhalten bei Laständerungen und Kommunikationsausfällen.

## Aktueller Stand

Die Kommunikation ist eingerichtet: Beide Boards führen MicroPython aus und haben jeweils eine MQTT-Statusmeldung über den lokalen Mosquitto-Broker an einen Fedora-Rechner gesendet.

| Bestandteil | Stand |
|---|---|
| USB-Zugriff auf beide MicroPython-Konsolen | Geprüft |
| MQTT-Veröffentlichung der Fertigung | Empfangen |
| MQTT-Veröffentlichung der Kühlung | Empfangen |
| Dauerhafter gleichzeitiger Sendebetrieb | Noch nicht getestet |

Maschinenmodelle und zentrale Python-Steuerung sind noch nicht implementiert. Der bisherige Test belegt den einzelnen Nachrichtenaustausch beider Boards.

## Aufbau

- **ESP32-S3 1 – Fertigung:** MQTT-Client `esp32-production`.
- **ESP32-S3 2 – Kühlung:** MQTT-Client `esp32-cooling`.
- **Fedora-Rechner:** Mosquitto-Broker und Terminal-Abonnent `mosquitto_sub`.
- **Verbindung:** USB für die Board-Konsolen, gemeinsames WLAN für MQTT.

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [Einrichtung](docs/01_setup.md) | Voraussetzungen, Board-Zugriff, WLAN und Broker |
| [MQTT-Kommunikation](docs/02_mqtt_communication.md) | Gerätekennungen, Testablauf und empfangene Nachrichten |
| [Fehlersuche](docs/troubleshooting.md) | Bekannte Probleme und gezielte Prüfungen |

Die [Beispielkonfiguration](mosquitto-dev.conf.example) dient als Vorlage für den lokalen Broker. Die angepasste Datei `mosquitto-dev.conf` bleibt außerhalb der Versionsverwaltung.

Dokumentationsstand: 27. Oktober 2026.
