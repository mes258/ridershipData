import json
import requests
import csv
import sys
sys.path.insert(0, "../../src")

from util import constants
from ridershipPatternScripts.routeSettings import RouteSettings
import routeDataAccessModule

class StopDataAccessModule:
  def __init__(self, routeSettings: RouteSettings):
    self.stopData = []
    self.routeSettings = routeSettings
    # This is need to get the stop order
    self.routeDataAM = routeDataAccessModule.RouteDataAccessModule(self.routeSettings)

  def readStopFile(self, year="", servicePeriod=""):
    if self.stopData == []:
      # See if there is a valid stops.txt file for the given service change
      stopData = []
      # If no year or service period is provided, default to the given values
      if year == "":
        year = self.routeSettings.year
      if servicePeriod == "":
        servicePeriod = self.routeSettings.servicePeriod
      stopDataFilePath = "../../data/stopData/kcm/{0}/{1}/stops.txt".format(year, servicePeriod)

      try: 
        with open(stopDataFilePath, mode='r', newline='') as infile:
          reader = csv.DictReader(infile)
          for row in reader:
            stopData.append(row)
      except:
        self.stopData = stopData
      self.stopData = stopData

  def getStopDataFromFile(self):
    # First try with the given year and service period. 
    self.readStopFile()
    if self.stopData == []:
      # stops.txt doesn't exist for the given service period, try using searching other time periods
      searchDistance = 1
      foundValidStopData = False
      givenSpIndex = constants.kcmServiceChangeNumbers.index(self.routeSettings.servicePeriod)

      while not foundValidStopData:
        # Try looking for a valid stop data file from before the current service change
        previousSpIndex = givenSpIndex + (-1 * searchDistance)
        if previousSpIndex >= 0:
          previousSp = constants.kcmServiceChangeNumbers[previousSpIndex]
          stopData = self.readStopFile(year=previousSp[:2], servicePeriod=previousSp)
          if stopData != []:
            self.stopData = stopData
            foundValidStopData = True
        # Try looking for a valid stop data file from after the current service change
        nextSpIndex = givenSpIndex + searchDistance
        if nextSpIndex < constants.kcmServiceChangeNumbers.count():
          nextSp = constants.kcmServiceChangeNumbers[nextSpIndex]
          stopData = self.readStopFile(year=nextSp[:2], servicePeriod=nextSp)
          if stopData != []:
            self.stopData = stopData
            foundValidStopData = True
          
        if previousSpIndex < 0 and nextSpIndex > constants.kcmServiceChangeNumbers.count():
          print("No vaild stop data")
          foundValidStopData = True

        # Increase the search distance for the next loop
        searchDistance += 1

  # The stop data for a route can change with a service changee, but it's generally fairly stable. 
  # For CT, the stop name is in the ridership data, so we don't have to worry about outdated stops. 
  # For ST and KCM, we will ideally a stops.txt file for the given service change. 
  # If not, we will search for the next closest stops.txt and use that instead.
  # Also, the stops.txt is from KCM. Despite it's file extension, it's formatted as a csv.
  def getStopNameForStopId(self, stopId):
        # For KCM/ST, stop data is stored in the stopData folder. CT already has the stop names in the ridership dataset
    # For kcm/st, use getStopDataFromFile(), for CT, use routeDataAM.getStopNameFromRidershipData()
    if self.routeSettings.agencyId == constants.ctAgencyId:
      return self.routeDataAM.getStopNameFromRidershipData(stopId)
    elif self.routeSettings.agencyId == constants.kcmAgencyId or self.routeSettings.agencyId == constants.stAgencyId:
      if self.stopData == []:
        self.getStopDataFromFile()
      for stopRow in self.stopData:
        if stopRow["stop_id"] == stopId:
          return stopRow["stop_name"]

    else:
      print("Unsupported agency id.")
      return ""

# Tests: 
# TODO: Move to a test class and add proper test cases
# testRouteSettings = RouteSettings("701", "24", "11", "Weekday", 29)
# testStopAM = StopDataAccessModule(testRouteSettings)
# testStopName = testStopAM.getStopNameForStopId("8300")
# print(testStopName)

# testRouteAM = routeDataAccessModule.RouteDataAccessModule(testRouteSettings)
# testStopIds = testRouteAM.getOrderedStops("I")
# print(testStopName)

# for id in testStopIds:
#   print(testStopAM.getStopNameForStopId(id))