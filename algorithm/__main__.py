import json
from math import asin, cos, radians, sin, sqrt
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "data.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# data is a dict; data["people"] is a list of dicts, one per person
people = data["people"]


def choose_drivers(people):
    """Pick the fewest drivers whose seats cover everyone (seats include the driver)."""
    # People without a car have no "seats" key, so .get(..., 0) treats them as 0
    car_owners = [p for p in people if p.get("seats", 0) > 0]
    car_owners.sort(key=lambda p: p["seats"], reverse=True)

    drivers = []
    capacity = 0
    for person in car_owners:
        if capacity >= len(people):
            break
        drivers.append(person)
        capacity += person["seats"]

    if capacity < len(people):
        raise ValueError(f"Not enough seats: {capacity} seats for {len(people)} people")
    return drivers


def distance_km(a, b):
    """Straight-line (haversine) distance between two people in km."""
    lat1, lon1, lat2, lon2 = map(radians, (a["lat"], a["lon"], b["lat"], b["lon"]))
    h = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * asin(sqrt(h))


def assign_passengers(people, drivers):
    """Greedily assign each passenger to a nearby driver with a free seat.

    Considers every (passenger, driver) pair from shortest to longest distance
    and accepts a pair if the passenger is unassigned and the car isn't full.
    """
    driver_ids = {d["id"] for d in drivers}
    passengers = [p for p in people if p["id"] not in driver_ids]

    # Each car's seats include the driver, so passengers get seats - 1
    cars = {d["id"]: {"driver": d, "passengers": [], "free": d["seats"] - 1} for d in drivers}

    pairs = sorted(
        ((distance_km(p, d), p, d) for p in passengers for d in drivers),
        key=lambda t: t[0],
    )

    assigned = set()
    for dist, p, d in pairs:
        car = cars[d["id"]]
        if p["id"] in assigned or car["free"] == 0:
            continue
        car["passengers"].append((p, dist))
        car["free"] -= 1
        assigned.add(p["id"])

    return cars


drivers = choose_drivers(people)
cars = assign_passengers(people, drivers)

total = 0
for car in cars.values():
    d = car["driver"]
    print(f"Car of {d['name']} (id {d['id']}):")
    for p, dist in car["passengers"]:
        print(f"  {p['name']} (id {p['id']}) walks {dist:.2f} km")
        total += dist
print(f"Total walking distance: {total:.2f} km")
