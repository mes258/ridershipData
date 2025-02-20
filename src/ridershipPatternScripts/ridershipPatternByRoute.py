from accessModules import routeDataAccessModule
from accessModules import stopDataAccessModule
from graphingScripts import graphModule
import routeSettings
from util import util

# Input: 
#   Route: Route to graph. For KCM RR, just use the letter (eg: "a", "e")
#   Year: Two digit year (eg: "24")
#   Service period: For KCM routes, put the SERVICE_CHANGE_NUM (eg: "213" or "241"). For CT routes, put the 2 digit month (eg: "08" or "11")
#   Day Type: "Weekday", "Saturday", or "Sunday". KCM only has "Weekday" data
#   Agency Id: KCM: 1, CT: 29, ST: 40
routeNum = "7"
year = "24"
servicePeriod = "241"
dayType = "Weekday"
agencyId = 1

route = routeSettings.RouteSettings(routeNum, year, servicePeriod, dayType, agencyId)

# Convert the RR route name to the underllying route number: a = 671, b = 672, etc. 
for letter, rapidRideRouteNum, shortName in stopDataAccessModule.rapidRideMappings:
  if letter in routeNum.lower():
    routeNum = rapidRideRouteNum
    break 

# Set up access module
am = routeDataAccessModule.RouteDataAccessModule(routeNum=routeNum, year=year, servicePeriod=servicePeriod, dayType=dayType)

# Per trip data
annual_AVG_TRIP_DEPARTING_LOAD = am.getColumnValuesPerStop("AVG_TRIP_DEPARTING_LOAD")
annual_AVG_TRIP_BOARDINGS = am.getColumnValuesPerStop("AVG_TRIP_BOARDINGS")
annual_AVG_TRIP_ALIGHTINGS = am.getColumnValuesPerStop("AVG_TRIP_ALIGHTINGS")

inboundLoadData, outboundLoadData = util.split_data_by_direction(annual_AVG_TRIP_DEPARTING_LOAD)
inboundTripBoardData, outboundTripBoardData = util.split_data_by_direction(annual_AVG_TRIP_BOARDINGS)
inboundTripAlightData, outboundTripAlightData = util.split_data_by_direction(annual_AVG_TRIP_ALIGHTINGS)

combinedInboundTripData = util.combine_dictionaries(inboundLoadData, inboundTripAlightData, inboundTripBoardData)
combinedOutboundTripData = util.combine_dictionaries(outboundLoadData, outboundTripAlightData, outboundTripBoardData)

# Per hour data
annual_AVG_TOTAL_BOARDINGS = am.getColumnValuesPerStop("AVG_TOTAL_BOARDINGS")
annual_AVG_TOTAL_ALIGHTINGS = am.getColumnValuesPerStop("AVG_TOTAL_ALIGHTINGS")

inboundTotalBoardData, outboundTotalBoardData = util.split_data_by_direction(annual_AVG_TOTAL_BOARDINGS)
inboundTotalAlightData, outboundTotalAlightData = util.split_data_by_direction(annual_AVG_TOTAL_ALIGHTINGS)

#inboundTotalLoadData = util.get_total_load_data(inboundTotalAlightData, inboundTotalBoardData)
combinedInboundTotalData = util.combine_dictionaries(inboundLoadData, inboundTotalAlightData, inboundTotalBoardData)
combinedOutboundTotalData = util.combine_dictionaries(outboundLoadData, outboundTotalAlightData, outboundTotalBoardData)


inboundDirection = "1"
outboundDirection = "0"

stopOrderInbound = stopDataAccessModule.getOrderedStops(routeNum, inboundDirection, year, servicePeriod)
stopOrderOutbound = stopDataAccessModule.getOrderedStops(routeNum, outboundDirection, year, servicePeriod)
print("Stop order inbound")
print(stopOrderInbound)
print(stopOrderOutbound)

print("combinedinboundtrip: ")
print(combinedInboundTripData)
if stopOrderInbound is not None:
  combinedInboundTripData = util.reorder_dict_with_prefix(reversed(stopOrderInbound), combinedInboundTripData)
  combinedInboundTotalData = util.reorder_dict_with_prefix(reversed(stopOrderInbound), combinedInboundTotalData)
if stopOrderOutbound is not None:
  combinedOutboundTripData = util.reorder_dict_with_prefix(stopOrderOutbound, combinedOutboundTripData)
  combinedOutboundTotalData = util.reorder_dict_with_prefix(stopOrderOutbound, combinedOutboundTotalData)


xAxisName = "Route {0} Stops".format(am.getFriendlyRouteNum())
totalBoardingsYAxisName = "Cumulative Boardings"
totalAlightingsYAxisName = "Cumulative Alightings"
totalTitle = "{0} per Trip for {1} Route {2}"

departureLoadYAxisName = "Average Ridership at Stop Departure per Trip"

routeName = "Route {0}".format(routeNum)

for letter, rapidRideRouteNum, shortName in stopDataAccessModule.rapidRideMappings:
  if routeNum == rapidRideRouteNum:
    routeName = shortName

departureLoadTitle = "Average Weekday Ridership per {0} Trip for {1} in 2023"

# Graphs for STB:
graphModule.plot_boarding_bars_and_dot_ridership(combinedInboundTripData, combinedOutboundTripData, am, False)
graphModule.plot_stacked_boarding_bars(combinedInboundTotalData, combinedOutboundTotalData, am)
