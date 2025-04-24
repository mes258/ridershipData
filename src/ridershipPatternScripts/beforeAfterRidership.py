import sys
sys.path.insert(0, "../../src")

from util import constants
from util import util
from ridershipPatternScripts.routeSettings import RouteSettings
from accessModules.routeDataAccessModule import RouteDataAccessModule
from accessModules.stopDataAccessModule import StopDataAccessModule
from graphingScripts.graphModule import plot_daily_ridership_before_after
import beforeAfterHelper


# Input: 
#   Route: Route to graph. For KCM RR, just use the letter (eg: "a", "e")
#   Year: Two digit year (eg: "24")
#   Service period: For KCM routes, put the SERVICE_CHANGE_NUM (eg: "213" or "241"). For CT routes, put the 2 digit month (eg: "08" or "11")
#   Day Type: "Weekday", "Saturday", or "Sunday". KCM only has "Weekday" data
#   Agency Id: KCM: 1, CT: 29, ST: 1 (ST should be 40 once I separate ST and KCM routes. For now, use 1 for ST. )
routeNum = "703"
agencyId = 29

# Before Data:
beforeYear = "24"
beforeServicePeriod = "08"
beforeDayType = "Weekday"

# After Data:
afterYear = "24"
afterServicePeriod = "11"
afterDayType = "Weekday"


# Convert the RR route name to the underllying route number: a = 671, b = 672, etc. 
for letter, rapidRideRouteNum, shortName in constants.namedRouteMappings:
  if letter in routeNum.lower():
    routeNum = rapidRideRouteNum
    break 

beforeRouteSettings = RouteSettings(routeNum, beforeYear, beforeServicePeriod, beforeDayType, agencyId)
afterRouteSettings = RouteSettings(routeNum, afterYear, afterServicePeriod, afterDayType, agencyId)

# Set up access modules
beforeRouteDataAM = RouteDataAccessModule(beforeRouteSettings)
afterRouteDataAM = RouteDataAccessModule(afterRouteSettings)
afterStopDataAM = StopDataAccessModule(afterRouteSettings)


beforeInboundData, beforeOutboundData = beforeAfterHelper.getInboundOutboundData(beforeRouteDataAM)
afterInboundData, afterOutboundData = beforeAfterHelper.getInboundOutboundData(afterRouteDataAM)


for letter, rapidRideRouteNum, shortName in constants.namedRouteMappings:
  if routeNum == rapidRideRouteNum:
    routeName = shortName


# Graphs for STB:
plot_daily_ridership_before_after(beforeInboundData, afterInboundData, beforeOutboundData, afterOutboundData, beforeRouteDataAM, afterRouteDataAM, afterStopDataAM)
