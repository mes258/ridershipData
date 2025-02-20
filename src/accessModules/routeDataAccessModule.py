import csv
import stopDataAccessModule
from util import constants
from ridershipPatternScripts import routeSettings

# Helper functions for getting data from the csvs. 
class RouteDataAccessModule:
  def __init__(self, routeSettings: routeSettings.RouteSettings):
    self.routeSettings = routeSettings
    self.filePath = "../../data/{0}RouteData/{1}/{2}/{3}/{4}/stopLevelData.csv".format(constants[self.routeSettings.agencyId], self.routeSettings.routeNum, self.routeSettings.year, self.routeSettings.servicePeriod, self.routeSettings.dayType)
      
  # Get all rows from the file path
  def getStopLevelData(self):
    stopLevelData = []
    try: 
      with open(self.filePath, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
          stopLevelData.append(row)
    except:
      #print("No data for {0}".format(self.filePath))
      return stopLevelData

    return stopLevelData
  
  def getFilteredRows(self, columnValues):
    filteredRows = []
    allRows = self.getStopLevelData()
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
    stopLevelData = self.getStopLevelData()
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
    for letter, rapidRideRouteNum, shortName in stopDataAccessModule.rapidRideMappings:
      if self.routeSettings.routeNum == rapidRideRouteNum:
        return shortName
    return self.routeSettings.routeNum
  
  # Use the cross streets to get the stop name. (not always accurate)
  def getStopNameFromStopId(self, stopId):
    stopLevelData = self.getStopLevelData()
    for entry in stopLevelData:
       if entry["STOP_ID"] == stopId:
          if self.routeNum[0] == "7":
            return entry["STOP_NAME"]
          else:
            return entry["HOST_STREET_NM"] + " / " + entry["CROSS_STREET_NM"]
    return None
  
