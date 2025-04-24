import sys
sys.path.insert(0, "../../src")

from util import constants
from util import util
from accessModules.routeDataAccessModule import RouteDataAccessModule

def getInboundOutboundData(routeDataAM: RouteDataAccessModule):
  annual_AVG_TRIP_DEPARTING_LOAD = routeDataAM.getColumnValuesPerStop("AVG_TRIP_DEPARTING_LOAD")

  inboundLoadData, outboundLoadData = util.split_data_by_direction(annual_AVG_TRIP_DEPARTING_LOAD)

  annual_AVG_TOTAL_BOARDINGS = routeDataAM.getColumnValuesPerStop("AVG_TOTAL_BOARDINGS")
  annual_AVG_TOTAL_ALIGHTINGS = routeDataAM.getColumnValuesPerStop("AVG_TOTAL_ALIGHTINGS")

  inboundTotalBoardData, outboundTotalBoardData = util.split_data_by_direction(annual_AVG_TOTAL_BOARDINGS)
  inboundTotalAlightData, outboundTotalAlightData = util.split_data_by_direction(annual_AVG_TOTAL_ALIGHTINGS)

  combinedInboundTotalData = util.combine_dictionaries(inboundLoadData, inboundTotalAlightData, inboundTotalBoardData)
  combinedOutboundTotalData = util.combine_dictionaries(outboundLoadData, outboundTotalAlightData, outboundTotalBoardData)

  stopOrderInbound = routeDataAM.getOrderedStops(constants.inboundDirection)
  stopOrderOutbound = routeDataAM.getOrderedStops(constants.outboundDirection)

  if stopOrderInbound is not None:
    combinedInboundTotalData = util.reorder_dict_with_prefix(reversed(stopOrderInbound), combinedInboundTotalData)
  if stopOrderOutbound is not None:
    combinedOutboundTotalData = util.reorder_dict_with_prefix(stopOrderOutbound, combinedOutboundTotalData)

  return combinedInboundTotalData, combinedOutboundTotalData
