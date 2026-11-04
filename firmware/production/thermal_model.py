def update_temperature(
    temperature,
    ambient,
    heating_power,
    cooling_power,
    heat_capacity,
    loss_coefficient,
    dt,
):
    """Berechnet einen Temperaturschritt aus der Wärmebilanz."""
    if heat_capacity <= 0:
        raise ValueError("Wärmekapazität muss positiv sein")

    if dt <= 0:
        raise ValueError("Zeitschritt muss positiv sein")

    heat_loss = loss_coefficient * (temperature - ambient)
    net_power = heating_power - heat_loss - cooling_power
    temperature_change = net_power * dt / heat_capacity

    return temperature + temperature_change
