# Entwicklungsverlauf

Diese Übersicht beschreibt die erreichten Meilensteine, ihre Nachweise und
wesentliche Erkenntnisse. Technische Einzelheiten stehen in der
[Einrichtung](01_setup.md) und der [MQTT-Dokumentation](02_mqtt_communication.md).
M1 und M2 wurden rückblickend aus den dokumentierten Tests zusammengefasst;
sie besitzen keine getrennten Implementierungs-Commits.

## M1 – Zugriff auf beide ESP32-S3

- **Ziel:** Python-Code auf beiden Boards ausführen können.
- **Änderung:** USB-Zugriff über `mpremote` und MicroPython-REPL eingerichtet.
- **Nachweis:** Beide Konsolen erreichbar; `umqtt.simple` auf beiden Boards importiert.
- **Erkenntnis:** REPL-Code läuft auf dem Board. Der Fedora-Rechner stellt über USB die Bedienoberfläche bereit.
- **Offen:** Der vollständige erfolgreiche Flash-Ablauf und die genaue Firmware-Version des Fertigungsboards sind nicht dokumentiert.
- **Git:** Grundaufbau in der ersten Dokumentation festgehalten: [05c1724](https://gitlab.bht-berlin.de/s90499/industrial_iot_ap/-/commit/05c17242585da8658ccbb5363d8b15a4b9ff532d).

## M2 – Manueller MQTT-Nachrichtenaustausch

- **Ziel:** Nachrichten beider Boards auf Fedora empfangen.
- **Änderung:** Mosquitto als lokalen Broker verwendet; getrennte Client-IDs und Status-Topics für Fertigung und Kühlung festgelegt.
- **Nachweis:** Beide manuell veröffentlichten Begrüßungen erschienen im Terminal-Abonnenten auf Fedora.
- **Erkenntnis:** Client-ID und Topic haben unterschiedliche Aufgaben: Verbindungskennung und Zuordnung der Nachricht. Eine falsche Gerätezuordnung wurde korrigiert.
- **Offen bei Abschluss:** Dauerhafter gemeinsamer Sendebetrieb und automatischer Start waren noch nicht getestet.
- **Git:** Testergebnis und Entwicklungsaufbau dokumentiert: [05c1724](https://gitlab.bht-berlin.de/s90499/industrial_iot_ap/-/commit/05c17242585da8658ccbb5363d8b15a4b9ff532d).

## M3 – Automatischer Sendebetrieb

- **Ziel:** Beide Boards ohne manuelle REPL-Befehle gemeinsam betreiben.
- **Änderung:** Gemeinsame `main.py`, gerätespezifische `config.py` und lokale, von Git ausgeschlossene `secrets.py` eingeführt.
- **Nachweis am 28.10.2026:** Nach Reset starteten beide Zähler bei 1. Gemeinsamer Empfang von 08:03:56 bis 08:06:16 beobachtet; beide Zähler stiegen von 22 auf 50.
- **Erkenntnis:** Programmstart, Geräteidentität und Zugangsdaten lassen sich getrennt verwalten. Der Sendetakt ist ungefähr fünf Sekunden und keine harte Echtzeitgarantie.
- **Offen:** Automatische Wiederverbindung bei WLAN- oder Broker-Ausfällen fehlt.
- **Git:** Firmware, Startanleitung und Ergebnisse versioniert: [29d190b](https://gitlab.bht-berlin.de/s90499/industrial_iot_ap/-/commit/29d190b475715ffdc1232c3ae7d42018c065267c).

## M4 – Strukturierte Nachrichten und Eingabeprüfung

- **Ziel:** Statusmeldungen auf Fedora automatisch interpretieren und prüfen.
- **Änderung:** JSON mit `device_id`, `session_id`, `seq` und `status` eingeführt; `tools/validate_status.py` ergänzt.
- **Nachweis am 28.10.2026:** Beide Gerätekennungen akzeptiert. Neue Sitzung nach Neustart des Fertigungsboards beobachtet. Falsche Kennung und ungültiges JSON abgewiesen; gültige Meldungen danach weiterverarbeitet.
- **Erkenntnis:** Syntaktisch gültiges JSON kann inhaltlich falsch sein. Topic und Gerätekennung müssen zusammenpassen; eine Sitzungskennung unterscheidet Programmläufe.
- **Offen:** Der Validator prüft einzelne Nachrichten, aber noch keine Sequenzlücken, Duplikate oder veralteten Sitzungen.
- **Git:** Dieser Eintrag wird zusammen mit JSON-Firmware und Validator im M4-Commit versioniert.

## M5 – Lokale Simulation von Fertigung und Kühlung

- **Ziel:** Temperaturentwicklung und verzögerte Kühlleistung nachvollziehbar simulieren.
- **Änderung:** Temperatur- und Kühlmodell als getrennte Funktionen implementiert. Ein Runner liest JSON-Szenarien, verarbeitet zeitgesteuerte Änderungen und gibt Temperatur sowie gelieferte Kühlleistung als CSV aus.
- **Nachweis:** Normalbetrieb, Lasterhöhung, konstante Kühlung und unmittelbarer Kühlungsausfall ausgeführt. Beide Modelle anschließend für Anlauf und normales Abschalten gekoppelt.
- **Ergebnisse:** Bei einer konstanten Kühlanforderung von 100 W stieg die Temperatur zunächst auf rund 25,333 °C und sank bis Sekunde 60 auf 24,401 °C. Nach Abschalten der Anforderung bei Sekunde 30 betrugen die Temperatur nach 60 Sekunden 26,418 °C und die verbleibende Kühlleistung 4,059 W.
- **Erkenntnis:** Angeforderte und gelieferte Kühlleistung unterscheiden sich. Normales Abschalten führt im Modell zu einem allmählichen Rückgang; ein vollständiger Kühlungsausfall wird dagegen als sofortiger Wegfall dargestellt.
- **Stand bei Abschluss von M5:** Die Parameter sind illustrative Beispielwerte, keine kalibrierten Messdaten. Die Modelle liefen lokal auf Fedora; Board-Integration und automatische Regelung folgten in M6.
- **Git:** Modelle, Runner, Szenarien und Dokumentation versioniert: [705f7d5](https://gitlab.bht-berlin.de/s90499/industrial_iot_ap/-/commit/705f7d5d58f8abc9208e41e6316c1d56cfab0087).

## M6 – Verteilter Regelkreis über MQTT

- **Ziel:** Fertigungsmodell, Kühlmodell und zentrale Regelung auf den vorgesehenen Rechnern verbinden.
- **Änderung:** Das Fertigungsboard berechnet und veröffentlicht seine Temperatur. Das Kühlungsboard verarbeitet Anforderungen und meldet seine gelieferte Leistung. Der Python-Controller auf Fedora fordert ab 28 °C eine Kühlleistung von 100 W und bis einschließlich 26 °C eine Leistung von 0 W an. Dazwischen bleibt die vorherige Anforderung bestehen. Gemeldete Kühlleistung wird an die Fertigung weitergeleitet; Mosquitto vermittelt sämtliche Nachrichten.
- **Nachweis:** Im beobachteten Lauf wurde bei 28,029 °C eingeschaltet. Die gelieferte Kühlung stieg schrittweise; die höchste angezeigte Temperatur betrug 28,273 °C. Bei 25,990 °C wurde ausgeschaltet. Die Temperatur sank kurzzeitig weiter bis 25,930 °C und stieg anschließend wieder. Der Ausschnitt endete bei 27,292 °C vor einer zweiten Einschaltung.
- **Erkenntnis:** Die Schaltschwellen lösen Entscheidungen aus, garantieren aber keine festen Temperaturgrenzen. Verzögerte Kühlwirkung und Nachrichtenübertragung beeinflussen den Verlauf.
- **Grenzen:** Der verbundene Normalbetrieb wurde demonstriert. Eingabevalidierung, Erkennung veralteter Daten, Schutzverhalten bei Controller-Ausfall und robuste Wiederverbindung des Gesamtsystems fehlen. Modellschritte verwenden eine feste Simulationszeit von einer Sekunde; längere Ausführungsverzögerungen werden nicht ausgeglichen. Der Controller verwendet Paho-Callbacks; asyncio und begrenzte Queues sind noch nicht integriert.
- **Git:** Firmware, Controller, Abhängigkeiten und Dokumentation sind für den gemeinsamen M6-Commit vorbereitet.
