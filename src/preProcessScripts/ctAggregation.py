import csv
from datetime import datetime
from collections import defaultdict
import os

def get_day_type(date):
    day = date.strftime("%A")
    if day == "Saturday":
        return "Saturday"
    elif day == "Sunday":
        return "Sunday"
    else:
        return "Weekday"

def get_time_period(time_str):
    time = datetime.strptime(time_str, "%H:%M:%S").time()
    if time < datetime.strptime("05:00:00", "%H:%M:%S").time():
        return "XNT"
    elif time < datetime.strptime("09:00:00", "%H:%M:%S").time():
        return "AM"
    elif time < datetime.strptime("15:00:00", "%H:%M:%S").time():
        return "MID"
    elif time < datetime.strptime("19:00:00", "%H:%M:%S").time():
        return "PM"
    elif time < datetime.strptime("22:00:00", "%H:%M:%S").time():
        return "XEV"
    else:
        return "XNT"
    
# For blue, green: north is inbound. For orange, east is inbound.
def get_direction_code(direction:str, routeId:str):
    if direction.lower() == "north" or direction.lower() == "east":
      return "I"
    else:
        return "O"

# Read CSV file
def get_input_data(filePath:str):
  data = []
  with open(filePath, "r") as file:
      reader = csv.DictReader(file)
      for row in reader:
          if row["ACTUAL_DEPARTURE_TIME"] and row["TRIP_ID"]:
              try:
                  date_obj = datetime.strptime(row["DATE"], "%m/%d/%Y").date()
                  row["DATE"] = date_obj
                  row["DAY_TYPE"] = get_day_type(date_obj)
                  row["ALIGHTINGS"] = int(row["ALIGHTINGS"])
                  row["BOARDINGS"] = int(row["BOARDINGS"])
                  row["TIME_PERIOD"] = get_time_period(row["ACTUAL_DEPARTURE_TIME"])
                  row["DIRECTION"] = get_direction_code(row["DIRECTION"], row["ROUTE_ID"])
                  data.append(row)
              except ValueError as e:
                  print(f"Skipping row due to error: {row} - {e}")
  return data

def populateDepartureLoad(data):
  departure_load = 0  # Initial load at the start of the route
  for row in data:
    boardings = int(row['BOARDINGS']) if row['BOARDINGS'] else 0
    alightings = int(row['ALIGHTINGS']) if row['ALIGHTINGS'] else 0
    
    if int(row['STOP_ORDER_NUMBER']) == 0:
       departure_load = boardings
    else:
       departure_load += boardings - alightings
    row['DEPARTURE_LOAD'] = departure_load

    # with open("departureLoadTest.csv", mode='a', newline='') as outfile:
    #   writer = csv.DictWriter(outfile, fieldnames=["DATE","ROUTE_ID","DIRECTION","TRIP_ID","VEHICLE_ID","SCHEDULED_TIME","ACTUAL_ARRIVAL_TIME","ACTUAL_DEPARTURE_TIME","STOP_ORDER_NUMBER","STOP_ID","STOP_NAME","BOARDINGS","ALIGHTINGS", "DAY_TYPE", "TIME_PERIOD", "DEPARTURE_LOAD"])
    #   writer.writerow(row)

  return data

def aggregateBoardingAndAlightingData(data):
  # Aggregate data
  aggregated_data = defaultdict(lambda: {"total_alightings": 0, "total_boardings": 0, "total_departure_load": 0, "trip_counts": [], "date_totals": defaultdict(int)})
  unique_dates = {"Weekday": set(), "Saturday": set(), "Sunday": set()}

  for row in data:
      key = (row["ROUTE_ID"], row["DIRECTION"], row["TIME_PERIOD"], row["STOP_ID"], row["STOP_NAME"], row["DAY_TYPE"], row['STOP_ORDER_NUMBER'])
      aggregated_data[key]["total_alightings"] += row["ALIGHTINGS"]
      aggregated_data[key]["total_boardings"] += row["BOARDINGS"]
      aggregated_data[key]["total_departure_load"] += row["DEPARTURE_LOAD"]
      aggregated_data[key]["trip_counts"].append(row["TRIP_ID"])
      aggregated_data[key]["date_totals"][row["DATE"]] += row["ALIGHTINGS"]
      unique_dates[row["DAY_TYPE"]].add(row["DATE"])

  # Compute averages and departing loads
  output_data = {"Weekday": [], "Saturday": [], "Sunday": []}
  trip_loads = defaultdict(lambda: defaultdict(int))  # { (route, direction, day_type, trip_id) -> { stop_id -> departing_load } }

  for key, values in aggregated_data.items():
      route, direction, time_period, stop_id, stop_name, day_type, stop_order_number = key
      num_days = len(unique_dates[day_type])
      num_unique_trips = len(values["trip_counts"])
      
      if num_days > 0 and num_unique_trips > 0:
          avg_total_alightings = values["total_alightings"] / num_days
          avg_trip_alightings = values["total_alightings"] / (num_unique_trips)
          avg_total_boardings = values["total_boardings"] / num_days
          avg_trip_boardings = values["total_boardings"] / (num_unique_trips)
          avg_trip_departing_load = values["total_departure_load"] / (num_unique_trips)
          
          output_data[day_type].append((*key, '%.3f'%(avg_trip_boardings), '%.3f'%(avg_total_boardings), '%.3f'%(avg_trip_alightings), '%.3f'%(avg_total_alightings), '%.3f'%(avg_trip_departing_load)))
  return output_data

def writeOutput(outputData, routeId, year, month):
  
  file_mapping = {"Weekday": "{0}/{1}/{2}/Weekday".format(routeId, year, month), "Saturday": "{0}/{1}/{2}/Saturday".format(routeId, year, month), "Sunday": "{0}/{1}/{2}/Sunday".format(routeId, year, month)}
  

  # Write results to CSV
  for day_type, filePath in file_mapping.items():
    fullFilePath = os.path.join("../../data/ctRouteData", filePath)
    os.makedirs(fullFilePath, exist_ok=True)
    fileName = os.path.join(fullFilePath, 'stopLevelData.csv')

    with open(fileName, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["SERVICE_RTE_NUM", "INBD_OUTBD_CD", "DAY_PART_CD", "STOP_ID", "STOP_NAME", "DAY_TYPE", "STOP_SEQUENCE_NUM", "AVG_TRIP_BOARDINGS", "AVG_TOTAL_BOARDINGS", "AVG_TRIP_ALIGHTINGS", "AVG_TOTAL_ALIGHTINGS", "AVG_TRIP_DEPARTING_LOAD"])
        writer.writerows(outputData[day_type])

    print(f"Output written to {fileName}")

def runAggregationForRoute(routeId, month, year):
  routeIdMapping = {"701": "Blue", "702": "Green", "703": "Orange"}
  monthMapping = {"08": "August", "11": "November"}

  fullFilePath = "../../data/rawData/ct/Swift_{0}_{1}_Full.csv".format(routeIdMapping[routeId], monthMapping[month]) 
  inputData = get_input_data(fullFilePath)
  dataWithDepartureLoads = populateDepartureLoad(inputData)
  #print(dataWithDepartureLoads[1])
  aggregatedData = aggregateBoardingAndAlightingData(dataWithDepartureLoads)
  writeOutput(aggregatedData, routeId, year, month)


# Edit these
# routeIds = ["701", "702", "703"]
# months = ["08", "11"]
# year = "24"

# for routeId in routeIds:
#    for month in months:
#       runAggregationForRoute(routeId, month, year)
