# Einrichtung

[Zur Übersicht](../README.md)

## Voraussetzungen

- Zwei ESP32-S3 mit funktionsfähiger MicroPython-REPL.
- Fedora-Rechner mit `mpremote`, Mosquitto und `mosquitto_sub`.
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

Anschließend müssen Board-Code und Terminal-Abonnent dieselbe Broker-Adresse verwenden. Im bisherigen Test war dies `192.168.178.28`; diese Adresse kann sich bei einem Netzwerkwechsel ändern.

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

Beide Boards verwenden [main.py](../firmware/main.py).
Nur die Gerätekennung und das Status-Topic unterscheiden sich:

| Rolle | Konfiguration im Repository | Dateiname auf dem Board |
|---|---|---|
| Fertigung | `firmware/production/config.py` | `config.py` |
| Kühlung | `firmware/cooling/config.py` | `config.py` |

Vor dem Übertragen mit `mpremote connect list` die Ports prüfen und den
physischen Boards zuordnen. Die folgenden Befehle setzen Fertigung an
`/dev/ttyACM0` und Kühlung an `/dev/ttyACM1` voraus.

**Fertigungsboard:**

```bash
mpremote connect /dev/ttyACM0 fs cp firmware/secrets.py :secrets.py
mpremote connect /dev/ttyACM0 fs cp firmware/production/config.py :config.py
mpremote connect /dev/ttyACM0 fs cp firmware/main.py :main.py
```

**Kühlungsboard:**

```bash
mpremote connect /dev/ttyACM1 fs cp firmware/secrets.py :secrets.py
mpremote connect /dev/ttyACM1 fs cp firmware/cooling/config.py :config.py
mpremote connect /dev/ttyACM1 fs cp firmware/main.py :main.py
```

Das Präfix `:` bezeichnet das Dateisystem des verbundenen Boards.
Die Befehle schreiben `secrets.py`, `config.py` und `main.py` in dessen
Hauptverzeichnis und ersetzen dort gleichnamige Dateien.
`boot.py` und die installierte MQTT-Bibliothek bleiben erhalten.
Die Vorlage `secrets.example.py` wird nicht auf die Boards kopiert.

## 6. Automatischen Start prüfen

1. Den Abonnenten in einem eigenen Fedora-Terminal starten. Die Beispieladresse
   durch die aktuelle Broker-Adresse ersetzen:

   ```bash
   mosquitto_sub -h 192.168.178.28 -t 'industrial/+/status' -v
   ```

2. Beide Boards über RESET/EN neu starten. MicroPython führt die jeweilige
   `main.py` automatisch aus.
3. Auf beiden Topics muss der Zähler bei `online 1` beginnen und ungefähr alle
   fünf Sekunden steigen. Beide Boards mindestens zwei Minuten beobachten.

Mit Strg-C endet der Terminal-Abonnent; die Boards senden weiter.
Testergebnis und Grenzen stehen unter [MQTT-Kommunikation](02_mqtt_communication.md).
