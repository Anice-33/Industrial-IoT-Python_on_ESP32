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
