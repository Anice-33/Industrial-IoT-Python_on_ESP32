# MQTT-Kommunikation

[Zur Übersicht](../README.md) · [Einrichtung](01_setup.md)

## Rollen und Topics

Mosquitto vermittelt alle Nachrichten. Der Controller ist ein eigener
MQTT-Client auf Fedora; die Boards verbinden sich nicht direkt miteinander.

| Sender → Empfänger über Mosquitto | Topic | Nutzdaten |
|---|---|---|
| Fertigung → Controller | `industrial/production/status` | Temperatur und angewendete Kühlung |
| Controller → Kühlung | `industrial/cooling/request` | Angeforderte Kühlleistung |
| Kühlung → Controller | `industrial/cooling/status` | Angeforderte und gelieferte Kühlleistung |
| Controller → Fertigung | `industrial/production/cooling` | Weitergeleitete gelieferte Kühlleistung |

Client-IDs: `esp32-production`, `esp32-cooling`, `fedora-controller`.
Die Client-ID kennzeichnet die Verbindung; das Topic bestimmt die
Nachrichtenzuordnung. Nur einen Controller mit dieser Kennung starten.

## Nachrichtenformat

Alle Payloads sind JSON-Objekte. Temperaturen werden in °C, Leistungen in W
übertragen. Die folgenden Werte sind Formatbeispiele, keine gemeinsame Messreihe.

**Fertigungsmeldung:**

```json
{"device_id":"esp32-production","session_id":"0123456789abcdef","seq":1,"status":"online","temperature_c":25.075,"applied_cooling_w":0.0}
```

**Kühlanforderung des Controllers:**

```json
{"requested_cooling_w":100.0}
```

**Kühlungsmeldung:**

```json
{"device_id":"esp32-cooling","session_id":"fedcba9876543210","seq":1,"status":"online","requested_cooling_w":100.0,"delivered_cooling_w":10.0}
```

**Weiterleitung an die Fertigung:**

```json
{"delivered_cooling_w":10.0}
```

Die Statusmeldungen behalten die M4-Felder:

| Feld | Bedeutung |
|---|---|
| `device_id` | Gerätekennung des sendenden Boards |
| `session_id` | Acht Zufallsbytes als 16 kleine Hexadezimalzeichen; einmal pro Programmlauf erzeugt |
| `seq` | Positive Ganzzahl; steigt je Veröffentlichung, beginnt nach Neustart bei 1 |
| `status` | Derzeit `online`; keine dauerhaft gültige Verfügbarkeitsgarantie |

`applied_cooling_w` zeigt, welche zuletzt empfangene Kühlleistung die Fertigung
für ihren Temperaturschritt verwendet hat. Die Kühlung meldet dagegen ihre
aktuelle Anforderung und die daraus berechnete Lieferung. Übertragungs- und
Ausführungszeitpunkte unterscheiden sich; Werte sind nicht atomar synchronisiert.

## Berechnung und Regelung

[main.py](../firmware/main.py) wählt anhand der Gerätekennung das Modell.
Die Fertigung startet bei 25 °C, mit 100 W Heizleistung, 20 °C Umgebung,
1000 J/K Wärmekapazität und 5 W/K Wärmeverlustkoeffizient. Die Kühlung startet
bei 0 W, hat maximal 100 W und eine Zeitkonstante von 10 s. Dies sind illustrative
Simulationsparameter, keine kalibrierten Messwerte.

Jedes Board prüft regelmäßig auf Eingaben und berechnet ungefähr einmal pro
Sekunde einen Modellschritt mit `dt=1.0`. Die Schleife pausiert jeweils 20 ms.
Längere Ausführungsverzögerungen werden nicht durch zusätzliche Schritte oder
angepasste Simulationszeit ausgeglichen.

[controller.py](../controller.py) verwendet Hysterese:

| Empfangene Temperatur | Kühlanforderung |
|---|---|
| ≥ 28 °C | 100 W |
| ≤ 26 °C | 0 W |
| Dazwischen | Vorherigen Wert beibehalten |

Die Anfangsanforderung ist 0 W. Bei jeder Temperaturmeldung veröffentlicht der
Controller die aktuelle Entscheidung. Bei jeder Kühlungsmeldung leitet er die
Lieferung an die Fertigung weiter. Er berechnet keines der beiden Modelle.
Die Implementierung verwendet Paho-Callbacks und `loop_forever()`, noch keine
asyncio-Tasks oder begrenzten Queues.

Aktuell werden Nachrichten mit QoS 0 und ohne Retain veröffentlicht.
Es gibt keine eigene Bestätigung, dass eine Anforderung bereits angewendet wurde.

## Beobachteter M6-Regelzyklus

Nach Upload der Modelle und Firmware wurde der gemeinsame Betrieb im
Controller-Terminal beobachtet:

| Beobachtung | Ergebnis |
|---|---|
| Erste Einschaltung | Bei 28,029 °C wechselte die Anforderung auf 100 W |
| Anlauf | Lieferung stieg über 10,00 → 19,00 → 27,10 W |
| Höchste angezeigte Temperatur | 28,273 °C, anschließend fallend |
| Ausschaltung | Bei 25,990 °C wechselte die Anforderung auf 0 W |
| Nachlauf | Lieferung sank über 89,99 → 80,99 → 72,89 W |
| Nachlauf der Temperatur | Tiefster angezeigter Wert 25,930 °C, danach erneute Erwärmung |
| Ende des Ausschnitts | 27,292 °C bei weiterhin 0 W Anforderung |

Die Schaltschwellen sind Entscheidungsgrenzen, keine garantierten Temperaturgrenzen.
Der Ausschnitt zeigt Einschalten, Abkühlen, Ausschalten und erneute Erwärmung;
eine zweite Einschaltung ist darin nicht enthalten. Ohne Zeitstempel lässt sich
daraus keine genaue Übertragungslatenz oder Zyklusdauer bestimmen.

## Empfang und ergänzende Statusprüfung

Alle vier Topics anzeigen (Broker-Adresse gegebenenfalls ersetzen):

```bash
mosquitto_sub -h 192.168.178.28 -t 'industrial/#' -v
```

Nur Board-Statusmeldungen mit dem bestehenden M4-Validator prüfen:

```bash
mosquitto_sub -h 192.168.178.28 -t 'industrial/+/status' -v |
python3 -u tools/validate_status.py
```

[validate_status.py](../tools/validate_status.py) liest Text über stdin und
prüft Topic, JSON-Objekt, Gerätekennung, Sitzungsformat, positive Sequenznummer
und Status. Es prüft nicht die neuen Modellwerte, Sequenzlücken, Duplikate oder
Aktualität. Diese Prüfung ist nicht in den Controller oder die Board-Empfänger
integriert. Die historischen M1–M5-Nachweise stehen im
[Entwicklungsverlauf](entwicklung.md).

## Grenzen des aktuellen Betriebs

Controller und Boards setzen passende JSON-Nachrichten voraus; fehlende oder
ungültige Felder können die Programme abbrechen lassen. Alte Statusmeldungen
ohne Modellfelder überspringt der Controller. Veraltete Eingaben werden nicht
erkannt: Nach Beenden des Controllers können die Boards ihre letzten Werte
weiterverwenden. Eine sichere Abschaltung und robuste Wiederherstellung des
gesamten Regelkreises nach Ausfällen sind noch nicht umgesetzt und nicht geprüft.
Der Broker verwendet die lokale Entwicklungskonfiguration ohne Authentifizierung
und TLS. Bei Problemen: [Fehlersuche](troubleshooting.md).
