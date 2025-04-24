from ctAggregation import get_input_data
from collections import defaultdict

# This file is for queries that rely on the detailed ridership data provided by CT. 
# It is currently set up to run the following methods for all Swift routes and print the results.
def getAverageDailyBoardings(inputData):
  dayTypeTotals = defaultdict(lambda: {'total_boardings': 0, 'day_counts': set()})
    
  for entry in inputData:
    day_type = entry['DAY_TYPE']
    boarding_count = entry['BOARDINGS']
    trip_date = entry['DATE']
        
    dayTypeTotals[day_type]['total_boardings'] += boarding_count
    dayTypeTotals[day_type]['day_counts'].add(trip_date)
    
  averages = {}
  for day_type, values in dayTypeTotals.items():
      unique_days = len(values['day_counts'])
      if unique_days > 0:
          averages[day_type] = values['total_boardings'] / unique_days
      else:
          averages[day_type] = 0
  print("Average Daily Ridership: ")
  print(averages)

def getTotalRidership(inputData):
  totalRidership = 0
    
  for entry in inputData:    
    totalRidership += entry['BOARDINGS']
    
  print(f"Total ridership: {totalRidership} ")

def getBusiestTrip(inputData):
  trip_totals = defaultdict(int)
    
  for entry in inputData:
    trip_id = entry['TRIP_ID']
    trip_date = entry['DATE']
    boarding_count = entry['BOARDINGS']
    
    trip_totals[(trip_id, trip_date)] += boarding_count
    
  busiest_trip = max(trip_totals.items(), key=lambda x: x[1], default=None)

  (trip_id, trip_date), total_boardings = busiest_trip
  print(f"Busiest Trip: TRIP_ID: {trip_id}, DATE: {trip_date}, TOTAL_BOARDINGS: {total_boardings}")

def getBusiestDay(inputData):
  day_totals = defaultdict(int)
    
  for entry in inputData:
    trip_date = entry['DATE']
    boarding_count = entry['BOARDINGS']
    
    day_totals[trip_date] += boarding_count
    
  busiest_day = max(day_totals.items(), key=lambda x: x[1], default=None)
    
  if busiest_day:
    trip_date, total_boardings = busiest_day
    print(f"Busiest Day: DATE: {trip_date}, TOTAL_BOARDINGS: {total_boardings}")


# Run CT Queries
routeIdMapping = {"701": "Blue", "702": "Green", "703": "Orange"}
monthMapping = {"08": "August", "11": "November"}
def runCtQueries(routeId, month):
  fullFilePath = "../../data/rawData/ct/Swift_{0}_{1}_Full.csv".format(routeIdMapping[routeId], monthMapping[month]) 
  inputData = get_input_data(fullFilePath)

  print(f"Stats for {routeIdMapping[routeId]} Line in {monthMapping[month]}")
  getTotalRidership (inputData)
  getAverageDailyBoardings(inputData)
  getBusiestTrip(inputData)
  getBusiestDay(inputData)


routeIds = ["701", "702", "703"]
months = ["08", "11"]

for routeId in routeIds:
   for month in months:
      runCtQueries(routeId, month)


