import argparse
import csv
import json
import math
import sys

from firmware.production.thermal_model import update_temperature
from firmware.cooling.cooling_model import update_cooling


parser = argparse.ArgumentParser(
    description="Führt ein thermisches Testszenario aus."
)
parser.add_argument("scenario", help="Pfad zur JSON-Szenariodatei")
args = parser.parse_args()

with open(args.scenario, encoding="utf-8") as file:
    scenario = json.load(file)

model = scenario["model"]
inputs = scenario["inputs"].copy()
events = scenario.get("events", [])
temperature = scenario["initial_state"]["temperature_c"]
dt = scenario["timing"]["step_s"]
duration = scenario["timing"]["duration_s"]
cooling_model = scenario.get("cooling_model")
delivered_cooling = scenario["initial_state"].get(
    "delivered_cooling_w", 0.0
)

if dt <= 0 or duration <= 0:
    raise ValueError("Zeitschritt und Dauer müssen positiv sein")

steps = round(duration / dt)

if not math.isclose(steps * dt, duration, rel_tol=0, abs_tol=1e-9):
    raise ValueError("Dauer muss ein ganzzahliges Vielfaches des Zeitschritts sein")

for event in events:
    event_time = event["at_s"]

    if not 0 <= event_time < duration:
        raise ValueError("Ereignis muss innerhalb der Simulationsdauer liegen")

    if not math.isclose(
        round(event_time / dt) * dt,
        event_time,
        rel_tol=0,
        abs_tol=1e-9,
    ):
        raise ValueError("Ereigniszeit muss auf einem Simulationsschritt liegen")

writer = csv.writer(sys.stdout)
writer.writerow(["time_s", "temperature_c", "delivered_cooling_w"])

initial_cooling = (
    delivered_cooling
    if cooling_model is not None
    else inputs["cooling_power_w"]
)
writer.writerow([0, temperature, initial_cooling])

for step in range(1, steps + 1):
    start_time = (step - 1) * dt

    for event in events:
        if math.isclose(
            event["at_s"], start_time, rel_tol=0, abs_tol=1e-9
        ):
            for field in (
                "heating_power_w",
                "cooling_power_w",
                "requested_cooling_w",
            ):
                if field in event:
                    inputs[field] = event[field]

    if cooling_model is not None:
        delivered_cooling = update_cooling(
            delivered_power=delivered_cooling,
            requested_power=inputs["requested_cooling_w"],
            max_power=cooling_model["max_power_w"],
            response_time=cooling_model["response_time_s"],
            dt=dt,
        )
    else:
        delivered_cooling = inputs["cooling_power_w"]

    temperature = update_temperature(
        temperature=temperature,
        ambient=model["ambient_temperature_c"],
        heating_power=inputs["heating_power_w"],
        cooling_power=delivered_cooling,
        heat_capacity=model["heat_capacity_j_per_k"],
        loss_coefficient=model["heat_loss_w_per_k"],
        dt=dt,
    )

    writer.writerow([step * dt, temperature, delivered_cooling])
