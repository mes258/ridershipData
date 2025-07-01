import requests
import json
import csv
import time
import polyline
from geopy.distance import geodesic


def getRouteId(routeNum):
  agencyId = 1
  if (routeNum[0] == "5" and len(routeNum) == 3):
    agencyId = 40
  url = "https://api.pugetsound.onebusaway.org/api/where/routes-for-agency/{0}.json".format(agencyId)
  api_key = "9b1e0a9c-2f8f-4bba-8343-3dce06819d03"

  params = {"key": api_key}

  response = requests.get(url, params=params)

  # Check that the request was successful (status code 200)
  if response.status_code == 200:
    all_route_data = json.loads(response.text)
    all_route_list = all_route_data["data"]["list"]
    for route in all_route_list:
      if route["shortName"] == routeNum:
        return route["id"]
      
  return None

def getRouteStops(routeNum, direction):
  routeId = getRouteId(routeNum)
  url = "https://api.pugetsound.onebusaway.org/api/where/stops-for-route/{0}.json".format(routeId)
  api_key = "9b1e0a9c-2f8f-4bba-8343-3dce06819d03"

  params = {"key": api_key}

  response = requests.get(url, params=params)

  # Check that the request was successful (status code 200)
  if response.status_code == 200:
    all_route_data = json.loads(response.text)
    stopGroups = all_route_data["data"]["entry"]["stopGroupings"][0]["stopGroups"]

    for sg in stopGroups:
      if sg["id"] == direction:
        return sg["stopIds"]
      
  return None


def getPolylineCoordinates(encodedPolyline):
  # Decode the polyline to get a list of (lat, lon) tuples
  coordinates = polyline.decode(encodedPolyline)
  #print(coordinates)
  return coordinates

def getPolylineLength(encodedPolyline):
  coordinates = getPolylineCoordinates(encodedPolyline)

  # Step 2: Compute the total length in kilometers
  total_length_km = sum(
      geodesic(coordinates[i], coordinates[i + 1]).kilometers
      for i in range(len(coordinates) - 1)
  )

  print(total_length_km)
  return total_length_km

def getLengthData(polylines):
  routeLen = 0.0
  for pl in polylines:
    length = getPolylineLength(pl["points"])
    routeLen += length

  crowFlyLen = 0.0
  startCoordinate = getPolylineCoordinates(polylines[0]["points"])[0]
  endCoordinate = getPolylineCoordinates(polylines[len(polylines) -1]["points"])[-1]
  print("Start: {0}; end: {1}".format(startCoordinate, endCoordinate))
  crowFlyLen = geodesic(startCoordinate, endCoordinate).kilometers
  
  if crowFlyLen == 0:
    lengthRatio = -1.0
  else:
    lengthRatio = routeLen / crowFlyLen
  polyLineCount = len(polylines)
  print("PolyLine count: {0}".format(polyLineCount))
  print("Ratio: {0}; Route length: {1}; Crow Fly Length: {2}".format(lengthRatio, routeLen, crowFlyLen)) #1_100263
  return routeLen, crowFlyLen, lengthRatio, polyLineCount


def getRouteLengths(routeNum):
  routeId = getRouteId(routeNum)
  if routeId is None:
    return None, None, None, None, None
  print(routeId)
  time.sleep(1)
  url = "https://api.pugetsound.onebusaway.org/api/where/stops-for-route/{0}.json".format(routeId)
  api_key = "9b1e0a9c-2f8f-4bba-8343-3dce06819d03"

  params = {"key": api_key}

  response = requests.get(url, params=params)

  # Check that the request was successful (status code 200)
  if response.status_code == 200:
    all_route_data = json.loads(response.text)
    stopGroups = all_route_data["data"]["entry"]["stopGroupings"][0]["stopGroups"]

    # Total for inbound + outbound
    totalRouteLen = 0.0
    totalCrowFlyLen = 0.0
    totalLengthRatio = 0.0
    totalPolyLineCount = 0.0
    for sg in stopGroups:
      polylines = sg["polylines"]
      routeLen, crowFlyLen, lengthRatio, polyLineCount = getLengthData(polylines)
      totalRouteLen += routeLen
      totalCrowFlyLen += crowFlyLen
      totalLengthRatio += lengthRatio
      totalPolyLineCount += polyLineCount

    # Get the averages:
    sgLen = len(stopGroups) 
    return totalRouteLen/sgLen, totalCrowFlyLen/sgLen, totalLengthRatio/sgLen, totalPolyLineCount, sgLen
  

allRouteData = []
rapidRides = ["A Line", "B Line", "C Line", "D Line", "E Line", "F Line", "G Line", "H Line"]
#for i in range(-8, 600):
for i in range(500, 600):
  routeNum = str(i)
  if i < 0:
    routeNum = rapidRides[i]
  print(routeNum)
  routeLen, crowFlyLen, lengthRatio, polyLineCount, stopGroupCount = getRouteLengths(routeNum)
  if routeLen is not None:
    allRouteData.append({"RouteNum": routeNum, "RouteLen": routeLen, "CrowFlyLen": crowFlyLen, "lengthRatio": lengthRatio, "polylineCount": polyLineCount, "stopGroupCount": stopGroupCount})

with open("routeLengthData1.csv", mode="w", newline="") as file:
    fieldnames = allRouteData[0].keys()
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(allRouteData)

# print(getRouteStops("545", "0")) #40_100236
