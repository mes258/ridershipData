import json
import requests
from util import constants

class StopDataAccessModule:
  def __init__(self, routeNum, year, servicePeriod, dayType):
    self.routeNum = routeNum
    self.year = year
    self.servicePeriod = servicePeriod
    self.dayType = dayType
    self.filePath = "{0}/{1}/{2}/{3}/stops.json".format(self.routeNum, self.year, self.servicePeriod, self.dayType)
    self.latestFilePath = "{0}/stops.json".format(self.routeNum)

  # The stop data for a route can change with a service changee, but it's generally fairly stable. 
  # To account for this, stop data is stored in at least two locations: 
  # The .filePath is a service change specific folder that will have the stop data for that service change. 
  #   This will be populated for all routes by a separate script once per service change. 
  # In case we don't have the stop data from that service change (eg: from 2023), the .latestFilePath will be populated by an API call. 
  def getAllStopLevelData(self):
    # First try to read from the path for this service change
    try:
      with open(self.filePath) as infile:
        if infile != None:
          return json.load(infile)
    except:
      # Next try to read from the general latest path
      try:
        with open(self.latestFilePath) as infile:
          if infile != None:
            return json.load(infile)
      except:
        # As a last resort, call the stops for route API to get the data and save the response in the .latestFilePath file.
        routeId = self.getRouteId()
        print("ROUTEID: {0}".format(routeId))
        url = "https://api.pugetsound.onebusaway.org/api/where/stops-for-route/{0}.json".format(routeId)
        api_key = ""
        params = {"key": api_key}
        response = requests.get(url, params=params)

        if response.status_code == 200:
          all_route_data = json.loads(response.text)
          with open(self.latestfilePath, "w") as outfile: 
            json.dump(all_route_data, outfile)
          return all_route_data
    
  def getOrderedStops(self, direction):
      key = "{0}_{1}_{2}_{3}".format(self.routeNum, direction, self.year, self.servicePeriod)
      print(key)
      if key in constants.hardCodedStops:
        return constants.hardCodedStops[key]
      else:
        try:
          allStopData = self.getAllStopLevelData()
          stopGroupings = allStopData["data"]["entry"]["stopGroupings"][0]["stopGroups"]
          for group in stopGroupings:
            if group["id"] == direction:
              return group["stopIds"]
        except:
          return None
      
  def getStopNameFromStopId(self, stopId):
    if self.routeNum[0] == "5":
      if stopId[:3] != "40_":
        stopId = "40_" + stopId
    if self.routeNum[0] == "7":
      raise ValueError('CT Route, will use name from csv. TODO: Fix this to avoid throwing exception.')
    else:
      if stopId[:2] != "1_":
        stopId = "1_" + stopId

    allStopData = self.getAllStopLevelData()
    allStops = allStopData["data"]["references"]["stops"]
    for stop in allStops:
      if stop["id"] == stopId:
        return stop["name"]
      
  def getRouteId(routeNum):
    for letter, rapidRideRouteNum, shortName in constants.rapidRideMappings:
      if routeNum == rapidRideRouteNum:
        routeNum = shortName
        break 

    agencyId = 1
    if routeNum[0] == "5":
      agencyId = 40
    if routeNum[0] == "7":
      agencyId = 29
    url = "https://api.pugetsound.onebusaway.org/api/where/routes-for-agency/{0}.json".format(agencyId)
    api_key = ""

    params = {"key": api_key}

    response = requests.get(url, params=params)

    if routeNum in constants.swiftMappings:
      routeNum = constants.swiftMappings[routeNum]

    # Check that the request was successful (status code 200)
    if response.status_code == 200:
      all_route_data = json.loads(response.text)
      all_route_list = all_route_data["data"]["list"]

      for route in all_route_list:
        if route["shortName"] == routeNum:
          return route["id"]
      
  #print(getAllStopLevelData("36"))
  #print(getOrderedStops("7", "1"))
  # print(getStopNameFromStopId("7", "1_1490"))
  # print(getStopNameFromStopId("7", "1610"))