# Industrial IoT: Vernetzte Fertigung und Kühlung

## Projektziel

Zwei ESP32-S3 sollen eine Fertigungsmaschine und eine Kühleinheit simulieren. Eine Python-Anwendung auf Linux soll ihre Zustände überwachen und die Kühlung steuern. Das Projekt untersucht das Verhalten bei Laständerungen und Kommunikationsausfällen.

## Aktueller Stand

Der verteilte Regelkreis läuft auf beiden ESP32-S3 und Fedora: Das
Fertigungsboard berechnet seine Temperatur, das Kühlungsboard seine gelieferte
Kühlleistung. Der Python-Controller auf Fedora entscheidet die Kühlanforderung
und leitet die gemeldete Kühlleistung an die Fertigung weiter. Mosquitto
vermittelt die Nachrichten.

| Bestandteil | Stand |
|---|---|
| Automatischer Start und JSON-Statusmeldungen beider Boards | Geprüft |
| Lokale Modellversuche mit sechs JSON-Szenarien | Ausgeführt |
| Temperatur- und Kühlmodell auf den jeweiligen Boards | Ausgeführt |
| Hystereseregelung: ab 28 °C an, bis einschließlich 26 °C aus | Normalbetrieb beobachtet |
| Einschalten, Abkühlen, Ausschalten und erneute Erwärmung | Im gemeinsamen Lauf beobachtet |
| Robuster Betrieb bei ungültigen Nachrichten und Ausfällen | Noch nicht abgesichert |

Die Leistungen und Temperaturen sind simuliert; es werden keine realen
Heiz- oder Kühlaktoren angesteuert. Die Parameter sind illustrative
Beispielwerte, keine kalibrierten Messdaten. Die Boards berechnen und senden
ungefähr einmal pro Sekunde; längere Verzögerungen werden nicht ausgeglichen.

## Aufbau

- **ESP32-S3 1 – Fertigung:** `esp32-production`; berechnet Temperatur aus Heizleistung, Wärmeverlust und zuletzt empfangener Kühlleistung.
- **ESP32-S3 2 – Kühlung:** `esp32-cooling`; nähert seine Lieferung schrittweise der angeforderten Leistung an.
- **Mosquitto auf Fedora:** Broker für alle vier Nachrichtenthemen.
- **Python-Controller auf Fedora:** `fedora-controller`; fordert 0 oder 100 W an und vermittelt gelieferte Kühlleistung an die Fertigung.
- **Verbindung:** Gemeinsames WLAN für MQTT, USB für Übertragung der Firmware und Board-Konsolen.

Nach der [Einrichtung](docs/01_setup.md) bei laufendem Broker starten
(Beispieladresse gegebenenfalls ersetzen):

```bash
.venv/bin/python controller.py --broker 192.168.178.28
```

Anschließend beide Boards über RESET/EN neu starten. Mit Strg-C endet der
Controller; das ist **keine Abschaltung der Boards**. Ohne neue Nachrichten
verwenden diese ihre zuletzt empfangenen Eingaben weiter.

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
| [Einrichtung](docs/01_setup.md) | Voraussetzungen, Firmware-Upload und Start des Regelkreises |
| [MQTT-Kommunikation](docs/02_mqtt_communication.md) | Topics, Nachrichtenfelder, Regelung und beobachteter Verlauf |
| [Fehlersuche](docs/troubleshooting.md) | Bekannte Probleme und gezielte Prüfungen |
| [Entwicklungsverlauf](docs/entwicklung.md) | Meilensteine, Nachweise, Erkenntnisse und Commit-Verweise |

Die [Beispielkonfiguration](mosquitto-dev.conf.example) dient als Vorlage für den lokalen Broker. Die angepasste Datei `mosquitto-dev.conf` bleibt außerhalb der Versionsverwaltung.

Dokumentationsstand: 4. November 2026.
