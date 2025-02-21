import csv
import sys
sys.path.insert(0, "../../src")
from util import constants
from ridershipPatternScripts.routeSettings import RouteSettings

# Helper functions for getting data from the csvs. 
class RouteDataAccessModule:
  def __init__(self, routeSettings: RouteSettings):
    self.routeSettings = routeSettings
    self.ridershipData = []
    self.ridershipDatafilePath = "../../data/{0}RouteData/{1}/{2}/{3}/{4}/stopLevelData.csv".format(constants.agencyIdAndInitials[self.routeSettings.agencyId], self.routeSettings.routeNum, self.routeSettings.year, self.routeSettings.servicePeriod, self.routeSettings.dayType)
      
  # Get all rows from the file path
  def getRidershipData(self):
    # If ridership data is empty, populate it, then return it. Otherwise, just return it.
    if self.ridershipData == []:
      stopLevelData = []
      try: 
        with open(self.ridershipDatafilePath, mode='r', newline='') as infile:
          reader = csv.DictReader(infile)
          for row in reader:
            stopLevelData.append(row)
      except:
        #print("No data for {0}".format(self.filePath))
        self.ridershipData = stopLevelData
      self.ridershipData = stopLevelData
    
    return self.ridershipData
  
  def getFilteredRows(self, columnValues):
    filteredRows = []
    allRows = self.getRidershipData()
    for row in allRows:
      validRow = True
      for columnName in columnValues:
        if row[columnName] != columnValues[columnName]:
          validRow = False
          break
      if validRow:
        filteredRows.append(row)
    return filteredRows
  
  # TODO: this function was written to average multiple service changes. Update it to be optimized for just one. 
  # Average the column's values over the 3 service changes in a year 
  def getColumnValuesPerStop(self, columnName):
    stopLevelData = self.getRidershipData()
    # Dictionary to store the total count and number of occurrences for each stop
    stop_totals = {}
    
    # Iterate through each object in the data list
    for entry in stopLevelData:
      # Unique stop id is inbound/outbound + stop id
      stop = str(entry['INBD_OUTBD_CD']) + str(entry['STOP_ID']) + str(entry['DAY_PART_CD'])
      count = float(entry[columnName])
      
      # If the stop is already in the dictionary, update its total and increment the count
      if stop in stop_totals:
          stop_totals[stop]['total'] += count
          stop_totals[stop]['serviceChangeCount'] += 1
      else:
          # If the stop is not in the dictionary, add it with the initial count
          stop_totals[stop] = {'total': count, 'serviceChangeCount': 1}
    
    # Calculate the average count per stop
    averages = {}
    for stop, values in stop_totals.items():
        averages[stop] = '%.3f'%(values['total'] / values['serviceChangeCount'])
        if averages[stop] == -1:
          print("-1 at: {0}".format(entry['STOP_ID']))
    
    return averages
  
  # Get the human readable route number (eg: 7 or E Line)
  # TODO: add swift support. 
  def getFriendlyRouteNum(self):
    for letter, rapidRideRouteNum, shortName in constants.rapidRideMappings:
      if self.routeSettings.routeNum == rapidRideRouteNum:
        return shortName
    return self.routeSettings.routeNum
  
  # Use the cross streets to get the stop name. (not always accurate)
  def getStopNameFromRidershipData(self, stopId):
    stopLevelData = self.getRidershipData()
    for entry in stopLevelData:
      if entry["STOP_ID"] == stopId:
        if "STOP_NAME" in entry:
          return entry["STOP_NAME"]
    # As a backup, just use the cross streets. 
    if "HOST_STREET_NM" in entry and "CROSS_STREET_NM" in entry:
      return entry["HOST_STREET_NM"] + " & " + entry["CROSS_STREET_NM"]
    return stopId
  
  # direction is "I" or "O"
  def getOrderedStops(self, direction):
    stopLevelData = self.getRidershipData()
  
    filtered_data = [entry for entry in stopLevelData if entry["INBD_OUTBD_CD"] == direction]

    # Extract unique stop IDs with their sequence numbers
    stop_sequence_map = {}
    for entry in filtered_data:
        stop_id = entry["STOP_ID"]
        try:
          stop_sequence = int(entry["STOP_SEQUENCE_NUM"])  # Convert to integer for sorting
          if stop_sequence not in stop_sequence_map:
              stop_sequence_map[stop_sequence] = stop_id 
        except:
          print("Invalid stop sequence for id: {0}. Will skip".format(stop_id))
          continue

    return [stop_sequence_map[seq] for seq in sorted(stop_sequence_map.keys())]


# Tests: 
# TODO: Move to a test class and add proper test cases
testRouteSettings = RouteSettings("7", "24", "241", "Weekday", 1)
testRouteAM = RouteDataAccessModule(testRouteSettings)
testStopIds = testRouteAM.getOrderedStops("I")
print(testStopIds)


  
