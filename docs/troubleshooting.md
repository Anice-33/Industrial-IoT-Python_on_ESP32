# Fehlersuche

[Zur Übersicht](../README.md)

## Bekannte Probleme

| Beobachtung | Ursache | Lösung und Ergebnis |
|---|---|---|
| Die Fertigung meldete sich unter dem Kühlungs-Topic | Kennung und Topic der Kühlung wurden auf dem Fertigungsboard wiederverwendet | Fertigungskennung und Fertigungs-Topic eingesetzt; Nachricht unter `industrial/production/status` empfangen |
| Der Abonnent zeigte nur `Hell` | Bereits der veröffentlichte Inhalt lautete `b"Hell"` | Vollständigen Text veröffentlicht; vollständiger Gruß empfangen |

Die zweite Beobachtung war kein nachgewiesener Übertragungsverlust. Zuerst den tatsächlich gesendeten Inhalt mit der empfangenen Ausgabe vergleichen.

## Keine MQTT-Nachricht empfangen

Die folgenden Schritte grenzen die Fehlerstelle ein:

1. **Richtiges Board:** Mit `mpremote connect list` die aktuellen Ports prüfen und die passende REPL öffnen. Portnamen können sich ändern.
2. **WLAN:** Auf dem Board die Verbindung prüfen:

   ```python
   import network
   wlan = network.WLAN(network.STA_IF)
   print(wlan.isconnected())
   print(wlan.ifconfig())
   ```

   Bei `False` zuerst die WLAN-Verbindung herstellen.

3. **Broker:** Auf Fedora den offenen Port prüfen:

   ```bash
   ss -ltnp 'sport = :1883'
   ```

   Der Broker muss auf einer vom Board erreichbaren Adresse lauschen. Nur `127.0.0.1` wäre für Zugriffe vom ESP32 ungeeignet.

4. **Adresse und Topic:** Die aktuelle Fedora-Adresse mit `server` im Board-Code und `-h` beim Abonnenten vergleichen. Den Filter `industrial/+/status` verwenden.
5. **Reihenfolge:** Den Abonnenten vor der Veröffentlichung starten und die Nachricht erneut senden.

Die ursprüngliche Broker-Adresse `192.168.178.28` ist netzabhängig und kann sich ändern.

## Doppelte Client-ID vermeiden

Fertigung und Kühlung benötigen unterschiedliche Client-IDs. Verbindet sich ein zweiter MQTT-Client mit derselben ID, ersetzt der Broker die ältere Verbindung.

Für die Fertigung `esp32-production`, für die Kühlung `esp32-cooling` verwenden. Ein solcher Verbindungsabbruch wurde im bisherigen Test nicht aufgezeichnet; die Regel erklärt, warum die Kennungen getrennt bleiben müssen.
