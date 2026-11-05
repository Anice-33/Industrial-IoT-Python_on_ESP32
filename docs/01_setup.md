# Einrichtung

[Zur Übersicht](../README.md)

## Voraussetzungen

- Zwei ESP32-S3 mit funktionsfähiger MicroPython-REPL.
- Fedora-Rechner mit Python 3, `venv`, `mpremote`, Mosquitto und `mosquitto_sub`.
- Paho MQTT für den Controller; Installation siehe Abschnitt 6.
- MQTT-Bibliothek `umqtt.simple` auf beiden Boards.
- Gemeinsames WLAN; die Boards müssen den Broker erreichen können.

Auf dem Kühlungsboard wurde MicroPython v1.29.0 vom 24.08.2026 ausgelesen. Für das Fertigungsboard ist keine genaue Firmware-Version dokumentiert. Ein vollständiger Flash-Ablauf ist bisher nicht festgehalten.

## 1. Board über USB öffnen

Im Fedora-Terminal verfügbare Ports anzeigen und die gewünschte Board-Konsole öffnen:

```bash
mpremote connect list
mpremote connect /dev/ttyACM0 repl
```

Im bisherigen Test war die Fertigung unter `/dev/ttyACM0` und die Kühlung unter `/dev/ttyACM1` erreichbar. Die Zuordnung kann sich nach erneutem Anschließen ändern.

Die Eingabeaufforderung `>>>` gehört zur MicroPython-Konsole des Boards. Dort eingegebener Python-Code läuft auf dem ESP32.

Version prüfen:

```python
import sys
print(sys.version)
```

Mit **Strg-]** oder **Strg-X** zur Fedora-Shell zurückkehren.

## 2. WLAN-Verbindung herstellen und prüfen

In der Board-Konsole ausführen. Die Platzhalter lokal durch die eigenen WLAN-Zugangsdaten ersetzen:

```python
import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("WLAN_NAME", "WLAN_PASSWORT")
time.sleep(5)
print(wlan.isconnected())
print(wlan.ifconfig())
```

Erst bei `True` mit dem MQTT-Test fortfahren. Andernfalls die Verbindung prüfen; fünf Sekunden Wartezeit garantieren noch keinen Verbindungsaufbau. Zugangsdaten gehören nicht ins Repository.

## 3. Broker auf Fedora prüfen

Die [Beispielkonfiguration](../mosquitto-dev.conf.example) im Repository als lokale Konfiguration kopieren:

```bash
cp -n mosquitto-dev.conf.example mosquitto-dev.conf
```

Den Befehl im Repository-Verzeichnis ausführen. `-n` verhindert das Überschreiben einer bereits vorhandenen lokalen Datei. `mosquitto-dev.conf` wird von Git ignoriert.

Die Vorlage bindet den Broker zunächst an `127.0.0.1` und ist damit nur auf dem Fedora-Rechner erreichbar. Für den Zugriff der ESP32 in der lokalen Datei `127.0.0.1` durch die aktuelle WLAN-IPv4-Adresse des Fedora-Rechners ersetzen. Verfügbare IPv4-Adressen anzeigen:

```bash
ip -4 address
```

Anschließend müssen Boards, Controller und Terminal-Abonnent dieselbe Broker-Adresse verwenden. Im bisherigen Test war dies `192.168.178.28`; diese Adresse kann sich bei einem Netzwerkwechsel ändern.

Den offenen Port im Fedora-Terminal prüfen:

```bash
ss -ltnp 'sport = :1883'
```

Im bisherigen Test wurde ein Mosquitto-Prozess auf `192.168.178.28:1883` angezeigt. Der genaue Startbefehl dieses Prozesses ist nicht dokumentiert.

Für einen erneuten Start mit der Projektkonfiguration kann im Repository-Verzeichnis folgender Befehl verwendet werden, sofern kein Broker auf derselben Adresse und demselben Port läuft:

```bash
mosquitto -c mosquitto-dev.conf -v
```

Die Konfiguration ist für den lokalen Entwicklungsaufbau bestimmt: Sie erlaubt anonymen Zugriff und richtet keine TLS-Verschlüsselung ein.

## 4. Lokale Firmware-Konfiguration anlegen

Alle folgenden Shell-Befehle im Repository-Verzeichnis ausführen.
Die [Vorlage](../firmware/secrets.example.py) als lokale Datei kopieren:

```bash
cp -n firmware/secrets.example.py firmware/secrets.py
```

In `firmware/secrets.py` die Platzhalter für WLAN-Name, WLAN-Passwort und
Broker-Adresse ersetzen. `MQTT_BROKER` muss die vom Board erreichbare
WLAN-IPv4-Adresse des Fedora-Rechners enthalten.
Die Datei bleibt lokal und wird durch `.gitignore` ausgeschlossen.
Die Vorlage enthält keine Zugangsdaten und wird versioniert.

Prüfen, dass die lokale Datei ignoriert wird:

```bash
git check-ignore -v firmware/secrets.py
```

## 5. Firmware auf beide Boards übertragen

Beide Boards verwenden [main.py](../firmware/main.py). Ihre `config.py`
legt Gerätekennung, Status-Topic und Eingangs-Topic fest. Die Gerätekennung
wählt das Modell und den Anfangszustand aus.

| Board | Konfiguration im Repository | Zusätzliches Modell auf dem Board |
|---|---|---|
| Fertigung | `firmware/production/config.py` | `thermal_model.py` |
| Kühlung | `firmware/cooling/config.py` | `cooling_model.py` |

Ports mit `mpremote connect list` prüfen und den physischen Boards zuordnen.
Die folgenden Befehle setzen Fertigung an `/dev/ttyACM0` und Kühlung an
`/dev/ttyACM1` voraus. Ein laufender Controller sollte während des Updates
beendet sein. `mpremote` kann die Ausführung auf dem Board unterbrechen.

Modell und Konfiguration zuerst, `main.py` zuletzt übertragen:

**Fertigungsboard:**

```bash
mpremote connect /dev/ttyACM0 fs cp firmware/secrets.py :secrets.py
mpremote connect /dev/ttyACM0 fs cp firmware/production/thermal_model.py :thermal_model.py
mpremote connect /dev/ttyACM0 fs cp firmware/production/config.py :config.py
mpremote connect /dev/ttyACM0 fs cp firmware/main.py :main.py
```

**Kühlungsboard:**

```bash
mpremote connect /dev/ttyACM1 fs cp firmware/secrets.py :secrets.py
mpremote connect /dev/ttyACM1 fs cp firmware/cooling/cooling_model.py :cooling_model.py
mpremote connect /dev/ttyACM1 fs cp firmware/cooling/config.py :config.py
mpremote connect /dev/ttyACM1 fs cp firmware/main.py :main.py
```

Das Präfix `:` bezeichnet das Dateisystem des verbundenen Boards.
Die Dateien liegen dort gemeinsam im Hauptverzeichnis; gleichnamige Dateien
werden ersetzt. Bereits passende `secrets.py` müssen nicht erneut übertragen
werden. `boot.py` und die installierte MQTT-Bibliothek bleiben erhalten.
Die Vorlage `secrets.example.py` wird nicht hochgeladen.

## 6. Controller auf Fedora vorbereiten

Im Repository-Verzeichnis:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Eine vorhandene Projektumgebung kann weiterverwendet werden.
[requirements.txt](../requirements.txt) enthält `paho-mqtt>=2.1,<3`;
im beobachteten Lauf war Version 2.1.0 installiert. `.venv/` wird von Git ignoriert.
Der Controller läuft auf Fedora, nicht auf den ESP32.

## 7. Gemeinsamen Regelbetrieb starten

1. Mosquitto mit der erreichbaren Projektadresse betreiben (Abschnitt 3).
   Keinen zweiten Broker auf demselben Port starten.
2. In einem weiteren Terminal genau einen Controller starten:

   ```bash
   .venv/bin/python controller.py --broker 192.168.178.28
   ```

3. Kühlungsboard, dann Fertigungsboard über RESET/EN neu starten.
   MicroPython startet die jeweilige `main.py` automatisch.
4. Im Controller Temperatur, Kühlanforderung und gemeldete Lieferung verfolgen.
   Die Fertigung beginnt bei 25 °C; die Kühlung beginnt mit 0 W Lieferung.
   Ab 28 °C wird 100 W angefordert, bis einschließlich 26 °C wieder 0 W.
   Zwischen den Schwellen bleibt die vorherige Entscheidung bestehen.
5. Mehrere Minuten beobachten: Lieferung baut sich auf, Temperatur sinkt,
   Lieferung klingt nach dem Ausschalten ab und Temperatur steigt erneut.

Optional alle vier Topics in einem zusätzlichen Terminal anzeigen:

```bash
mosquitto_sub -h 192.168.178.28 -t 'industrial/#' -v
```

Jedes Board veröffentlicht ungefähr einmal pro Sekunde. `seq` beginnt pro
Programmlauf bei 1; `session_id` wird beim Start neu erzeugt. Empfang und
Modellschritte beider Boards sind nicht zeitlich synchronisiert.

Strg-C beendet den Controller, nicht die Boards. Es gibt noch keine
Zeitüberschreitung für veraltete Eingaben und keine automatische Schutzabschaltung:
Boards können mit der letzten Eingabe weiterrechnen. Für einen definierten
Neustart Controller starten und beide Boards zurücksetzen.

Nachrichtenvertrag und beobachtete Ergebnisse:
[MQTT-Kommunikation](02_mqtt_communication.md).
