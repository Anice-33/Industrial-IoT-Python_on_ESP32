def update_cooling(
    delivered_power,
    requested_power,
    max_power,
    response_time,
    dt,
):
    """Berechnet die gelieferte Kühlleistung für einen Zeitschritt."""
    if max_power <= 0:
        raise ValueError("Maximale Kühlleistung muss positiv sein")

    if response_time <= 0:
        raise ValueError("Zeitkonstante muss positiv sein")

    if not 0 < dt <= response_time:
        raise ValueError("Zeitschritt muss positiv und höchstens die Zeitkonstante sein")

    if not 0 <= delivered_power <= max_power:
        raise ValueError("Gelieferte Kühlleistung liegt außerhalb der Grenzen")

    target = min(max(requested_power, 0.0), max_power)
    response_fraction = dt / response_time

    return delivered_power + response_fraction * (target - delivered_power)
