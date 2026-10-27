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

Anschließend den [MQTT-Test](02_mqtt_communication.md) durchführen.
