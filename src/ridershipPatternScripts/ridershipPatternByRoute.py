import sys
sys.path.insert(0, "../../src")

from util import constants
from util import util
from ridershipPatternScripts.routeSettings import RouteSettings
from accessModules.routeDataAccessModule import RouteDataAccessModule
from accessModules.stopDataAccessModule import StopDataAccessModule
from graphingScripts.graphModule import plot_trip_ridership, plot_daily_ridership


# Input: 
#   Route: Route to graph. For KCM RR, just use the letter (eg: "a", "e")
#   Year: Two digit year (eg: "24")
#   Service period: For KCM routes, put the SERVICE_CHANGE_NUM (eg: "213" or "241"). For CT routes, put the 2 digit month (eg: "08" or "11")
#   Day Type: "Weekday", "Saturday", or "Sunday". KCM only has "Weekday" data
#   Agency Id: KCM: 1, CT: 29, ST: 1 (ST should be 40 once I separate ST and KCM routes. For now, use 1 for ST. )
routeNum = "50"
year = "24"
servicePeriod = "241"
dayType = "Weekday"
agencyId = 1


# Convert the RR route name to the underllying route number: a = 671, b = 672, etc. 
for letter, rapidRideRouteNum, shortName in constants.namedRouteMappings:
  if letter in routeNum.lower():
    routeNum = rapidRideRouteNum
    break 

routeSettings = RouteSettings(routeNum, year, servicePeriod, dayType, agencyId)

# Set up access modules
routeDataAM = RouteDataAccessModule(routeSettings)
stopDataAM = StopDataAccessModule(routeSettings)

# Per trip data
annual_AVG_TRIP_DEPARTING_LOAD = routeDataAM.getColumnValuesPerStop("AVG_TRIP_DEPARTING_LOAD")
annual_AVG_TRIP_BOARDINGS = routeDataAM.getColumnValuesPerStop("AVG_TRIP_BOARDINGS")
annual_AVG_TRIP_ALIGHTINGS = routeDataAM.getColumnValuesPerStop("AVG_TRIP_ALIGHTINGS")

inboundLoadData, outboundLoadData = util.split_data_by_direction(annual_AVG_TRIP_DEPARTING_LOAD)
inboundTripBoardData, outboundTripBoardData = util.split_data_by_direction(annual_AVG_TRIP_BOARDINGS)
inboundTripAlightData, outboundTripAlightData = util.split_data_by_direction(annual_AVG_TRIP_ALIGHTINGS)

combinedInboundTripData = util.combine_dictionaries(inboundLoadData, inboundTripAlightData, inboundTripBoardData)
combinedOutboundTripData = util.combine_dictionaries(outboundLoadData, outboundTripAlightData, outboundTripBoardData)

annual_AVG_TOTAL_BOARDINGS = routeDataAM.getColumnValuesPerStop("AVG_TOTAL_BOARDINGS")
annual_AVG_TOTAL_ALIGHTINGS = routeDataAM.getColumnValuesPerStop("AVG_TOTAL_ALIGHTINGS")

inboundTotalBoardData, outboundTotalBoardData = util.split_data_by_direction(annual_AVG_TOTAL_BOARDINGS)
inboundTotalAlightData, outboundTotalAlightData = util.split_data_by_direction(annual_AVG_TOTAL_ALIGHTINGS)

combinedInboundTotalData = util.combine_dictionaries(inboundLoadData, inboundTotalAlightData, inboundTotalBoardData)
combinedOutboundTotalData = util.combine_dictionaries(outboundLoadData, outboundTotalAlightData, outboundTotalBoardData)

stopOrderInbound = routeDataAM.getOrderedStops(constants.inboundDirection)
stopOrderOutbound = routeDataAM.getOrderedStops(constants.outboundDirection)

if stopOrderInbound is not None:
  combinedInboundTripData = util.reorder_dict_with_prefix(reversed(stopOrderInbound), combinedInboundTripData)
  combinedInboundTotalData = util.reorder_dict_with_prefix(reversed(stopOrderInbound), combinedInboundTotalData)
if stopOrderOutbound is not None:
  combinedOutboundTripData = util.reorder_dict_with_prefix(stopOrderOutbound, combinedOutboundTripData)
  combinedOutboundTotalData = util.reorder_dict_with_prefix(stopOrderOutbound, combinedOutboundTotalData)


for letter, rapidRideRouteNum, shortName in constants.namedRouteMappings:
  if routeNum == rapidRideRouteNum:
    routeName = shortName


# Graphs for STB:
plot_trip_ridership(combinedInboundTripData, combinedOutboundTripData, routeDataAM, stopDataAM)
plot_daily_ridership(combinedInboundTotalData, combinedOutboundTotalData, routeDataAM, stopDataAM)
