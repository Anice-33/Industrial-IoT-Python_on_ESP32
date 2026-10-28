# Industrial IoT: Vernetzte Fertigung und Kühlung

## Projektziel

Zwei ESP32-S3 sollen eine Fertigungsmaschine und eine Kühleinheit simulieren. Eine Python-Anwendung auf Linux soll ihre Zustände überwachen und die Kühlung steuern. Das Projekt untersucht das Verhalten bei Laständerungen und Kommunikationsausfällen.

## Aktueller Stand

Beide ESP32-S3 starten nach einem Reset automatisch und veröffentlichen
etwa alle fünf Sekunden eine MQTT-Statusmeldung im JSON-Format mit
Gerätekennung, Sitzungskennung und Sequenznummer. Mosquitto auf Fedora
leitet die Nachrichten weiter; ein Python-Werkzeug prüft ihren Aufbau.

| Bestandteil | Stand |
|---|---|
| USB-Zugriff auf beide MicroPython-Konsolen | Geprüft |
| MQTT-Veröffentlichung beider Boards | Geprüft |
| Automatischer Programmstart nach Reset | Geprüft |
| Gleichzeitiger Sendebetrieb über mehr als zwei Minuten | Geprüft |
| JSON-Nachrichten beider Boards auf Fedora validiert | Geprüft |
| Ungültige Nachrichten abgewiesen; Verarbeitung läuft weiter | Geprüft |
| Automatische Wiederverbindung nach Ausfällen | Noch nicht umgesetzt |

Maschinenmodelle und zentrale Python-Steuerung sind noch nicht implementiert.
Der aktuelle Firmware-Stand prüft die Kommunikation.

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
| [Entwicklungsverlauf](docs/entwicklung.md) | Meilensteine, Nachweise, Erkenntnisse und Commit-Verweise |

Die [Beispielkonfiguration](mosquitto-dev.conf.example) dient als Vorlage für den lokalen Broker. Die angepasste Datei `mosquitto-dev.conf` bleibt außerhalb der Versionsverwaltung.

Dokumentationsstand: 28. Oktober 2026.
