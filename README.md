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
| Lokales Temperatur- und Kühlmodell mit JSON-Szenarien | Implementiert und ausgeführt |
| Gekoppelter Anlauf und normales Abschalten der Kühlung | Lokal geprüft |
| Automatische Wiederverbindung nach Ausfällen | Noch nicht umgesetzt |

Temperatur- und Kühlmodell laufen bisher lokal auf Fedora. Ein Szenario-Runner
verarbeitet vorgegebene Eingaben und gibt die Ergebnisse als CSV aus.
Die Parameter sind illustrative Beispielwerte, keine kalibrierten Messdaten.
Die ESP32-Firmware veröffentlicht weiterhin Statusmeldungen. Die Integration
der Modelle auf den Boards und die zentrale Python-Regelung sind noch nicht umgesetzt.

## Aufbau

- **ESP32-S3 1 – Fertigung:** MQTT-Client `esp32-production`.
- **ESP32-S3 2 – Kühlung:** MQTT-Client `esp32-cooling`.
- **Fedora-Rechner:** Mosquitto-Broker, Terminal-Abonnent `mosquitto_sub`, Statusvalidator und lokaler Szenario-Runner.
- **Verbindung:** USB für die Board-Konsolen, gemeinsames WLAN für MQTT.

## Lokale Simulation ausführen

Im Repository-Verzeichnis mit Python 3 ausführen; Boards und Broker sind dafür nicht erforderlich:

```bash
python3 -m tools.run_thermal_scenario tests/scenarios/gekoppelter_betrieb.json
```

Die CSV-Ausgabe enthält simulierte Zeit, Temperatur und gelieferte Kühlleistung.
Das Szenario `abschalten_kuehlung.json` setzt die Kühlanforderung nach 30 Sekunden
auf null. Die gelieferte Kühlleistung sinkt anschließend allmählich.
Weitere Szenarien behandeln Normalbetrieb, Lasterhöhung, konstante Kühlung
und unmittelbaren Kühlungsausfall.

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [Einrichtung](docs/01_setup.md) | Voraussetzungen, Board-Zugriff, WLAN und Broker |
| [MQTT-Kommunikation](docs/02_mqtt_communication.md) | Gerätekennungen, Testablauf und empfangene Nachrichten |
| [Fehlersuche](docs/troubleshooting.md) | Bekannte Probleme und gezielte Prüfungen |
| [Entwicklungsverlauf](docs/entwicklung.md) | Meilensteine, Nachweise, Erkenntnisse und Commit-Verweise |

Die [Beispielkonfiguration](mosquitto-dev.conf.example) dient als Vorlage für den lokalen Broker. Die angepasste Datei `mosquitto-dev.conf` bleibt außerhalb der Versionsverwaltung.

Dokumentationsstand: 4. November 2026.
