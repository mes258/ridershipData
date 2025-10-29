import csv

def calculate_train_load(data, direction="south"):
    """
    Calculate number of passengers on a train at each stop.
    """
    if direction == "south":
        stops = sorted(data, key=lambda x: int(x["stationCode"]))
    elif direction == "north":
        stops = sorted(data, key=lambda x: int(x["stationCode"]), reverse=True)
    else:
        raise ValueError("direction must be 'south' or 'north'")

    onboard = 0
    result = []

    for stop in stops:
        north = int(stop["North"])
        south = int(stop["South"])

        if direction == "south":
            boardings = south
            alightings = north
        else:  # northbound
            boardings = north
            alightings = south

        onboard += boardings - alightings
        onboard = max(onboard, 0)

        result.append({
            "Station": stop["Station"],
            "Direction": direction,
            "Boardings": boardings,
            "Alightings": alightings,
            "Onboard": onboard
        })

    return result


def process_csv(input_file):
    # Read CSV
    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]

    # Calculate loads
    southbound = calculate_train_load(data, "south")
    northbound = calculate_train_load(data, "north")

    # Combine results
    results = southbound + northbound

    print(results)


process_csv("../../data/stRouteData/1 Line/25/5/Weekday/perDirectionLinkBoardings.csv")
