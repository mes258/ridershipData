import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgba
import numpy as np
from collections import OrderedDict
import os
import sys
import calendar
sys.path.insert(0, "../../src")

from util import constants
from util import util
from ridershipPatternScripts.routeSettings import RouteSettings
from accessModules.routeDataAccessModule import RouteDataAccessModule
from accessModules.stopDataAccessModule import StopDataAccessModule
import csv


#AM - 5AM-9AM, MID - 9AM-3PM, PM - 3PM-7PM, XEV - 7PM - 10PM, XNT 10PM - 5AM
time_order_color = [['5am-9am (AM)', 'y'], ['9am-3pm (MID)', 'b'], ['3pm-7pm (PM)', 'g'], ['7pm-10pm (XEV)', 'm'], ['10pm-5am (XNT)', 'k']]
light_time_order_color = [(to_rgba(c[1], alpha=0.5)) for c in time_order_color]

# Set the stop name label size based on the number of stops. 
def getAxisLabelSize(inboundStopCount, outboundStopCount):
    maxStopCount = max(inboundStopCount, outboundStopCount)
    return -0.2 * maxStopCount + 30

def plot_trip_ridership(inbound_sorted_data, outbound_sorted_data, routeDataAM: RouteDataAccessModule, stopDataAM: StopDataAccessModule):
    # Before setting up the plot, create all the labels: 
    routeName = "Route {0}".format(routeDataAM.routeSettings.routeNum)
    for letter, rapidRideRouteNum, shortName in constants.namedRouteMappings:
      if routeDataAM.routeSettings.routeNum == rapidRideRouteNum:
        routeName = shortName

    # At this point, route name is either "Route N" or "X Line"
    # Need Overall title, per chart title, per chart y axis label, x axis label
    overallTitle = "Average Weekday Ridership per {0} Trip in 20{1}".format(routeName, routeDataAM.routeSettings.year)
    inboundTitle = "Inbound Trips"
    outboundTitle = "Outbound Trips"
    inboundYAxis = "{0} Inbound Stops (Read Down)".format(routeName)
    outboundYAxis = "{0} Outbound Stops (Read Up)".format(routeName)
    xAxis = "Passenger Count"

    mainTitleSize = 40
    subTitleSize = 30
    axisLabelSizeValue = min(getAxisLabelSize(len(inbound_sorted_data), len(outbound_sorted_data)), 20)
    axisLabelSize = axisLabelSizeValue 
    axisIncrementsSize = axisLabelSizeValue
    legendTextSize = 15

    
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(30, 20))
    plt.rc('xtick', labelsize=12)     
    plt.rc('ytick', labelsize=12)
    ax1.set_xlabel(xAxis, fontsize=axisLabelSize)
    ax1.set_ylabel(inboundYAxis, fontsize=axisLabelSize)
    ax1.set_title(inboundTitle, fontsize=subTitleSize)
    ax1.tick_params(axis='x', labelsize=axisIncrementsSize)
    ax1.tick_params(axis='y', labelsize=axisIncrementsSize)

    ax2.set_xlabel(xAxis, fontsize=axisLabelSize)
    ax2.set_ylabel(outboundYAxis, fontsize=axisLabelSize)
    ax2.set_title(outboundTitle, fontsize=subTitleSize)
    ax2.tick_params(axis='x', labelsize=axisIncrementsSize)
    ax2.tick_params(axis='y', labelsize=axisIncrementsSize)

    
    ax1.set_xlim(-10, 30)  # Set x-axis limits
    ax2.set_xlim(-10, 30) # Set x-axis limits
    
    fig.suptitle(overallTitle, fontsize=mainTitleSize)

    ax1.grid(True)
    ax2.grid(True)
    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)
    time_order_color = [['5am-9am (AM)', 'y', 4], ['9am-3pm (MID)', 'b', 6], ['3pm-7pm (PM)', 'g', 4], ['7pm-10pm (XEV)', 'm', 3], ['10pm-5am (XNT)', 'k', 7]]

    # Define time periods for reference and spacing
    time_offset = np.linspace(-0.3, 0.3, len(time_order_color))  # Create a small offset for the y positions
    
    # INBOUND DATA:
    maxPositive = 0 # boarding
    maxNegative = 0 # alightings
    firstDot = True
    # Iterate over each key in the data dictionary
    for i, (y_label, values) in enumerate(inbound_sorted_data.items()):
        for j, (dot, neg_bar, pos_bar) in enumerate(values):
            if dot == -1:
              continue

            if dot > maxPositive:
              maxPositive = dot
            if neg_bar > maxNegative:
              maxNegative = neg_bar

            # Calculate the y position with an offset for each time period
            y_pos = i + time_offset[j] * -1

            # Add dummy dots for the legend to be sorted correctly
            if firstDot:
              firstDot = False
              for t_o_color in time_order_color:
                ax1.plot(500, y_pos, 'o' + t_o_color[1], label=f'{t_o_color[0]}', markersize=6)
            
            # Plot dot for the first value (with slight vertical spacing for time periods)
            ax1.plot(dot, y_pos, 'o' + time_order_color[j][1], label=f'{time_order_color[j][0]}', markersize=7)

            # Plot negative bar for the second value and positive bar for the third value
            ax1.barh(y_pos, -neg_bar, color=time_order_color[j][1], height=0.15, align='center')
            ax1.barh(y_pos, pos_bar, color=time_order_color[j][1], height=0.15, align='center')

    # Set the y-ticks to the keys in the dictionary
    x = list(inbound_sorted_data.keys())
    for i in range(len(x)):
      # Populate stop names
      x[i] = stopDataAM.getStopNameForStopId(x[i])

    ax1.set_yticks(range(len(x)))
    ax1.set_yticklabels(x)

    # OUTBOUND DATA: 
    firstDot = True
    # Iterate over each key in the data dictionary
    for i, (y_label, values) in enumerate(outbound_sorted_data.items()):
        for j, (dot, neg_bar, pos_bar) in enumerate(values):
            if dot == -1:
              continue
            
            if dot > maxPositive:
              maxPositive = dot
            if neg_bar > maxNegative:
              maxNegative = neg_bar

            # Calculate the y position with an offset for each time period
            y_pos = i + time_offset[j] * -1

            # Add dummy dots for the legend to be sorted correctly
            if firstDot:
              firstDot = False
              for t_o_color in time_order_color:
                ax2.plot(500, y_pos, 'o' + t_o_color[1], label=f'{t_o_color[0]}', markersize=6)
          
            # Plot dot for the first value (with slight vertical spacing for time periods)
            ax2.plot(dot, y_pos, 'o' + time_order_color[j][1], label=f'{time_order_color[j][0]}', markersize=7)

            # Plot negative bar for the second value and positive bar for the third value
            ax2.barh(y_pos, -neg_bar, color=time_order_color[j][1], height=0.15, align='center')
            ax2.barh(y_pos, pos_bar, color=time_order_color[j][1], height=0.15, align='center')
            

    # Set the y-ticks to the keys in the dictionary
    x = list(outbound_sorted_data.keys())
    for i in range(len(x)):
      x[i] = stopDataAM.getStopNameForStopId(x[i])

    ax2.set_yticks(range(len(x)))
    ax2.set_yticklabels(x)

    lowerLimit = (maxNegative + 0.1 * maxNegative) * -1
    upperLimit = maxPositive + 0.1 * maxPositive
    ax1.set_xlim(lowerLimit, upperLimit)  # Set x-axis limits
    ax2.set_xlim(lowerLimit, upperLimit) # Set x-axis limits

    handles, labels = plt.gca().get_legend_handles_labels()
    order = [0,1,2,3,4]
    ax2.legend([handles[idx] for idx in order],[labels[idx] for idx in order], fontsize=legendTextSize)
    ax1.legend([handles[idx] for idx in order],[labels[idx] for idx in order], fontsize=legendTextSize)
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # This reserves space for the suptitle

    plt.subplots_adjust(top=0.92)

    #plt.show()
    # eg: src/graphs/kcm/7/24/241/Weekday/TripRidership.png
    directory = f"../../graphs/{constants.agencyIdAndInitials[routeDataAM.routeSettings.agencyId]}/{routeDataAM.routeSettings.routeNum}/{routeDataAM.routeSettings.year}/{routeDataAM.routeSettings.servicePeriod}/{routeDataAM.routeSettings.dayType}"
    os.makedirs(directory, exist_ok=True)
    output_file = os.path.join(directory, 'TripRidership.png')
    fig.savefig(output_file)   # save the plot to file
    plt.close(fig)


def plot_daily_ridership(inbound_sorted_data, outbound_sorted_data, routeDataAM: RouteDataAccessModule, stopDataAM: StopDataAccessModule):
   # Before setting up the plot, create all the labels: 
    routeName = "Route {0}".format(routeDataAM.routeSettings.routeNum)
    for letter, rapidRideRouteNum, shortName in constants.namedRouteMappings:
      if routeDataAM.routeSettings.routeNum == rapidRideRouteNum:
        routeName = shortName

    # At this point, route name is either "Route N" or "X Line"
    # Need Overall title, per chart title, per chart y axis label, x axis label
    overallTitle = "Average Daily Stop Ridership for {0} in 20{1}".format(routeName, routeDataAM.routeSettings.year)
    inboundTitle = "Inbound Trips"
    outboundTitle = "Outbound Trips"
    inboundYAxis = "{0} Inbound Stops (Read Down)".format(routeName)
    outboundYAxis = "{0} Outbound Stops (Read Up)".format(routeName)
    xAxis = "Passenger Count"

    mainTitleSize = 40
    subTitleSize = 30
    axisLabelSizeValue = min(getAxisLabelSize(len(inbound_sorted_data), len(outbound_sorted_data)), 20)
    axisLabelSize = axisLabelSizeValue 
    axisIncrementsSize = axisLabelSizeValue
    legendTextSize = 15
    barSize = 0.6

    
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(30, 20))
    plt.rc('xtick', labelsize=12)     
    plt.rc('ytick', labelsize=12)
    ax1.set_xlabel(xAxis, fontsize=axisLabelSize)
    ax1.set_ylabel(inboundYAxis, fontsize=axisLabelSize)
    ax1.set_title(inboundTitle, fontsize=subTitleSize)
    ax1.tick_params(axis='x', labelsize=axisIncrementsSize)
    ax1.tick_params(axis='y', labelsize=axisIncrementsSize)

    ax2.set_xlabel(xAxis, fontsize=axisLabelSize)
    ax2.set_ylabel(outboundYAxis, fontsize=axisLabelSize)
    ax2.set_title(outboundTitle, fontsize=subTitleSize)
    ax2.tick_params(axis='x', labelsize=axisIncrementsSize)
    ax2.tick_params(axis='y', labelsize=axisIncrementsSize)
    
    fig.suptitle(overallTitle, fontsize=mainTitleSize)

    ax1.grid(True)
    ax2.grid(True)
    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)
    time_order_color = [['5am-9am (AM)', 'y', 4], ['9am-3pm (MID)', 'b', 6], ['3pm-7pm (PM)', 'g', 4], ['7pm-10pm (XEV)', 'm', 3], ['10pm-5am (XNT)', 'k', 7]]

    # Set the y-ticks to the keys in the dictionary
    x = list(inbound_sorted_data.keys())
    for i in range(len(x)):
      x[i] = stopDataAM.getStopNameForStopId(x[i])

    ax1.set_yticks(range(len(x)))
    ax1.set_yticklabels(x)

    maxPositiveStopTotal = 0 # boarding
    maxNegativeStopTotal = 0 # alightings
    firstDot = True
    # Iterate over each key in the data dictionary
    for i, (y_label, values) in enumerate(inbound_sorted_data.items()):
      if firstDot:
        firstDot = False
        for t_o_color in time_order_color:
          ax1.barh(i, 5, color=t_o_color[1], label=f'{t_o_color[0]}', left=5000)

      # values: [[ridership, alights, boards],[ridership, alights, boards],..]
      amData = values[0]
      midData = values[1]
      pmData = values[2]
      evData = values[3]
      ntData = values[4]
      # Inbound alights
      ax1.barh(i, -amData[1], color=time_order_color[0][1], height=barSize, align='center')
      ax1.barh(i, -midData[1], left=-amData[1], color=time_order_color[1][1], height=barSize, align='center')
      ax1.barh(i, -pmData[1], left=-amData[1]-midData[1], color=time_order_color[2][1], height=barSize, align='center')
      ax1.barh(i, -evData[1], left=-amData[1]-midData[1]-pmData[1], color=time_order_color[3][1], height=barSize, align='center')
      ax1.barh(i, -ntData[1], left=-amData[1]-midData[1]-pmData[1]-evData[1], color=time_order_color[4][1], height=barSize, align='center')
      if amData[1]+midData[1]+pmData[1]+evData[1]+ntData[1] > maxNegativeStopTotal:
         maxNegativeStopTotal = amData[1]+midData[1]+pmData[1]+evData[1]+ntData[1]

      # Inbound boardings
      ax1.barh(i, amData[2], color=time_order_color[0][1], height=barSize, align='center')
      ax1.barh(i, midData[2], left=amData[2], color=time_order_color[1][1], height=barSize, align='center')
      ax1.barh(i, pmData[2], left=amData[2]+midData[2], color=time_order_color[2][1], height=barSize, align='center')
      ax1.barh(i, evData[2], left=amData[2]+midData[2]+pmData[2], color=time_order_color[3][1], height=barSize, align='center')
      ax1.barh(i, ntData[2], left=amData[2]+midData[2]+pmData[2]+evData[2], color=time_order_color[4][1], height=barSize, align='center')

      if amData[2]+midData[2]+pmData[2]+evData[2]+ntData[2] > maxPositiveStopTotal:
         maxPositiveStopTotal = amData[2]+midData[2]+pmData[2]+evData[2]+ntData[2]

    # OUTBOUOND Data
    # Set the y-ticks to the keys in the dictionary
    x = list(outbound_sorted_data.keys())
    for i in range(len(x)):
      x[i] = stopDataAM.getStopNameForStopId(x[i])

    ax2.set_yticks(range(len(x)))
    ax2.set_yticklabels(x)

    firstDot = True
    for i, (y_label, values) in enumerate(outbound_sorted_data.items()):
      if firstDot:
        firstDot = False
        for t_o_color in time_order_color:
          ax2.barh(i, 5, color=t_o_color[1], label=f'{t_o_color[0]}', left=5000)

      # values: [[ridership, alights, boards],[ridership, alights, boards],..]
      amData = values[0]
      midData = values[1]
      pmData = values[2]
      evData = values[3]
      ntData = values[4]
      # Inbound alights
      ax2.barh(i, -amData[1], color=time_order_color[0][1], height=barSize, align='center')
      ax2.barh(i, -midData[1], left=-amData[1], color=time_order_color[1][1], height=barSize, align='center')
      ax2.barh(i, -pmData[1], left=-amData[1]-midData[1], color=time_order_color[2][1], height=barSize, align='center')
      ax2.barh(i, -evData[1], left=-amData[1]-midData[1]-pmData[1], color=time_order_color[3][1], height=barSize, align='center')
      ax2.barh(i, -ntData[1], left=-amData[1]-midData[1]-pmData[1]-evData[1], color=time_order_color[4][1], height=barSize, align='center')
            
      if amData[1]+midData[1]+pmData[1]+evData[1]+ntData[1] > maxNegativeStopTotal:
         maxNegativeStopTotal = amData[1]+midData[1]+pmData[1]+evData[1]+ntData[1]

      # Inbound boardings
      ax2.barh(i, amData[2], color=time_order_color[0][1], height=barSize, align='center')
      ax2.barh(i, midData[2], left=amData[2], color=time_order_color[1][1], height=barSize, align='center')
      ax2.barh(i, pmData[2], left=amData[2]+midData[2], color=time_order_color[2][1], height=barSize, align='center')
      ax2.barh(i, evData[2], left=amData[2]+midData[2]+pmData[2], color=time_order_color[3][1], height=barSize, align='center')
      ax2.barh(i, ntData[2], left=amData[2]+midData[2]+pmData[2]+evData[2], color=time_order_color[4][1], height=barSize, align='center')

      if amData[2]+midData[2]+pmData[2]+evData[2]+ntData[2] > maxPositiveStopTotal:
         maxPositiveStopTotal = amData[2]+midData[2]+pmData[2]+evData[2]+ntData[2]

    print(maxNegativeStopTotal)
    print(maxPositiveStopTotal)
    lowerLimit = (maxNegativeStopTotal + 0.1 * maxNegativeStopTotal) * -1
    upperLimit = maxPositiveStopTotal + 0.1 * maxPositiveStopTotal
    ax1.set_xlim(lowerLimit, upperLimit)  # Set x-axis limits
    ax2.set_xlim(lowerLimit, upperLimit) # Set x-axis limits
    ax1.legend(fontsize=legendTextSize)
    ax2.legend(fontsize=legendTextSize)
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # This reserves space for the suptitle

    plt.subplots_adjust(top=0.92)

    # eg: src/graphs/kcm/7/24/241/Weekday/TripRidership.png
    directory = f"../../graphs/{constants.agencyIdAndInitials[routeDataAM.routeSettings.agencyId]}/{routeDataAM.routeSettings.routeNum}/{routeDataAM.routeSettings.year}/{routeDataAM.routeSettings.servicePeriod}/{routeDataAM.routeSettings.dayType}"
    os.makedirs(directory, exist_ok=True)
    output_file = os.path.join(directory, 'DailyRidership.png')
    fig.savefig(output_file)   # save the plot to file

# index: 1 = alightings, 2 = boardings
def getTotalCount(values, index):
  sum = '%.3f'%(values[0][index] + values[1][index] + values[2][index] + values[3][index] + values[4][index])
  return sum

def printStopValues(stopId, before_values, after_values, direction, stopDataAM: StopDataAccessModule):
  stopName = stopDataAM.getStopNameForStopId(stopId)
  # print as a CSV: stopName, direction, beforeBoardings, beforeAlightings, afterBoardings, afterAlightings
  print(f"{stopName},{direction},{getTotalCount(before_values, 2)},{getTotalCount(before_values, 1)},{getTotalCount(after_values, 2)},{getTotalCount(after_values, 1)}")

# Before and after
def plot_daily_ridership_before_after(inbound_before, inbound_after, outbound_before, outbound_after, beforeRouteDataAM: RouteDataAccessModule, afterRouteDataAM: RouteDataAccessModule, stopDataAM: StopDataAccessModule):
   # Before setting up the plot, create all the labels: 
    routeName = "Route {0}".format(afterRouteDataAM.routeSettings.routeNum)
    for letter, rapidRideRouteNum, shortName in constants.namedRouteMappings:
      if afterRouteDataAM.routeSettings.routeNum == rapidRideRouteNum:
        routeName = shortName

    beforeMonth = calendar.month_name[int(beforeRouteDataAM.routeSettings.servicePeriod)]
    afterMonth = calendar.month_name[int(afterRouteDataAM.routeSettings.servicePeriod)]

    # At this point, route name is either "Route N" or "X Line"
    # Need Overall title, per chart title, per chart y axis label, x axis label
    overallTitle = "Average Daily Stop Ridership for {0} in {1} and {2} 20{3}".format(routeName, beforeMonth, afterMonth, afterRouteDataAM.routeSettings.year)
    inboundTitle = "Inbound Trips"
    outboundTitle = "Outbound Trips"
    inboundYAxis = "{0} Inbound Stops (Read Down)".format(routeName)
    outboundYAxis = "{0} Outbound Stops (Read Up)".format(routeName)
    xAxis = "Passenger Count"

    mainTitleSize = 40
    subTitleSize = 30
    axisLabelSizeValue = min(getAxisLabelSize(len(inbound_after), len(inbound_before)), 20)
    axisLabelSize = axisLabelSizeValue 
    axisIncrementsSize = axisLabelSizeValue
    legendTextSize = 15
    barSize = 0.6

    
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(30, 20))
    plt.rc('xtick', labelsize=12)     
    plt.rc('ytick', labelsize=12)
    ax1.set_xlabel(xAxis, fontsize=axisLabelSize)
    ax1.set_ylabel(inboundYAxis, fontsize=axisLabelSize)
    ax1.set_title(inboundTitle, fontsize=subTitleSize)
    ax1.tick_params(axis='x', labelsize=axisIncrementsSize)
    ax1.tick_params(axis='y', labelsize=axisIncrementsSize)

    ax2.set_xlabel(xAxis, fontsize=axisLabelSize)
    ax2.set_ylabel(outboundYAxis, fontsize=axisLabelSize)
    ax2.set_title(outboundTitle, fontsize=subTitleSize)
    ax2.tick_params(axis='x', labelsize=axisIncrementsSize)
    ax2.tick_params(axis='y', labelsize=axisIncrementsSize)
    
    fig.suptitle(overallTitle, fontsize=mainTitleSize)

    ax1.grid(True)
    ax2.grid(True)
    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)

    time_order_color = [['5am-9am', 'y'], ['9am-3pm', 'b'], ['3pm-7pm', 'g'], ['7pm-10pm', 'm'], ['10pm-5am', 'k']]

    offset = barSize/4
    barSize = barSize/2

    # INBOUND data
    # Set the y-ticks to the keys in the dictionary
    stopIds = list(inbound_after.keys())
    stopNames = []
    for i in range(len(stopIds)):
      stopNames.append(stopDataAM.getStopNameForStopId(stopIds[i]))

    ax1.set_yticks(range(len(stopNames)))
    ax1.set_yticklabels(stopNames)

    maxPositiveStopTotal = 0 # boarding
    maxNegativeStopTotal = 0 # alightings
    firstDot = True
    # Iterate over each key in the data dictionary
    for i, stopId in enumerate(stopIds):
      if firstDot:
        firstDot = False
        for t_o_color in time_order_color:
          ax1.barh(i, 5, color=t_o_color[1], label=f'{beforeMonth} {t_o_color[0]}', left=5000, alpha=0.5)
          ax1.barh(i, 5, color=t_o_color[1], label=f'{afterMonth} {t_o_color[0]}', left=5000)


      before_values = []
      after_values = []

      # Fix renamed stops manually for now.
      if stopId == "3313":
        # Swift Blue changed stop id at Aurora Village TC
        before_values = inbound_before["2742"]
      elif stopId == "3382":
        # Swift Blue did not stop at Shoreline north before, so all data is zero
        before_values = [[0 for _ in range(3)] for _ in range(5)]
      else:
        before_values = inbound_before[stopId]
      after_values = inbound_after[stopId]

      printStopValues(stopId, before_values, after_values, "inbound", stopDataAM)

      # before values: [[ridership, alights, boards],[ridership, alights, boards],..]
      amDataB = before_values[0]
      midDataB = before_values[1]
      pmDataB = before_values[2]
      evDataB = before_values[3]
      ntDataB = before_values[4]
      # Inbound alights before
      ax1.barh(i + offset, -amDataB[1], color=time_order_color[0][1], height=barSize, align='center', alpha=0.5)
      ax1.barh(i + offset, -midDataB[1], left=-amDataB[1], color=time_order_color[1][1], height=barSize, align='center', alpha=0.5)
      ax1.barh(i + offset, -pmDataB[1], left=-amDataB[1]-midDataB[1], color=time_order_color[2][1], height=barSize, align='center', alpha=0.5)
      ax1.barh(i + offset, -evDataB[1], left=-amDataB[1]-midDataB[1]-pmDataB[1], color=time_order_color[3][1], height=barSize, align='center', alpha=0.5)
      ax1.barh(i + offset, -ntDataB[1], left=-amDataB[1]-midDataB[1]-pmDataB[1]-evDataB[1], color=time_order_color[4][1], height=barSize, align='center', alpha=0.5)
      if amDataB[1]+midDataB[1]+pmDataB[1]+evDataB[1]+ntDataB[1] > maxNegativeStopTotal:
         maxNegativeStopTotal = amDataB[1]+midDataB[1]+pmDataB[1]+evDataB[1]+ntDataB[1]

      # after values: [[ridership, alights, boards],[ridership, alights, boards],..]
      amDataA = after_values[0]
      midDataA = after_values[1]
      pmDataA = after_values[2]
      evDataA = after_values[3]
      ntDataA = after_values[4]
      # Inbound alights after
      ax1.barh(i - offset, -amDataA[1], color=time_order_color[0][1], height=barSize, align='center')
      ax1.barh(i - offset, -midDataA[1], left=-amDataA[1], color=time_order_color[1][1], height=barSize, align='center')
      ax1.barh(i - offset, -pmDataA[1], left=-amDataA[1]-midDataA[1], color=time_order_color[2][1], height=barSize, align='center')
      ax1.barh(i - offset, -evDataA[1], left=-amDataA[1]-midDataA[1]-pmDataA[1], color=time_order_color[3][1], height=barSize, align='center')
      ax1.barh(i - offset, -ntDataA[1], left=-amDataA[1]-midDataA[1]-pmDataA[1]-evDataA[1], color=time_order_color[4][1], height=barSize, align='center')
      if amDataA[1]+midDataA[1]+pmDataA[1]+evDataA[1]+ntDataA[1] > maxNegativeStopTotal:
         maxNegativeStopTotal = amDataA[1]+midDataA[1]+pmDataA[1]+evDataA[1]+ntDataA[1]


      # Inbound boardings before
      ax1.barh(i + offset, amDataB[2], color=time_order_color[0][1], height=barSize, align='center', alpha=0.5)
      ax1.barh(i + offset, midDataB[2], left=amDataB[2], color=time_order_color[1][1], height=barSize, align='center', alpha=0.5)
      ax1.barh(i + offset, pmDataB[2], left=amDataB[2]+midDataB[2], color=time_order_color[2][1], height=barSize, align='center', alpha=0.5)
      ax1.barh(i + offset, evDataB[2], left=amDataB[2]+midDataB[2]+pmDataB[2], color=time_order_color[3][1], height=barSize, align='center', alpha=0.5)
      ax1.barh(i + offset, ntDataB[2], left=amDataB[2]+midDataB[2]+pmDataB[2]+evDataB[2], color=time_order_color[4][1], height=barSize, align='center', alpha=0.5)

      if amDataB[2]+midDataB[2]+pmDataB[2]+evDataB[2]+ntDataB[2] > maxPositiveStopTotal:
         maxPositiveStopTotal = amDataB[2]+midDataB[2]+pmDataB[2]+evDataB[2]+ntDataB[2]


       # Inbound boardings after
      ax1.barh(i - offset, amDataA[2], color=time_order_color[0][1], height=barSize, align='center')
      ax1.barh(i - offset, midDataA[2], left=amDataA[2], color=time_order_color[1][1], height=barSize, align='center')
      ax1.barh(i - offset, pmDataA[2], left=amDataA[2]+midDataA[2], color=time_order_color[2][1], height=barSize, align='center')
      ax1.barh(i - offset, evDataA[2], left=amDataA[2]+midDataA[2]+pmDataA[2], color=time_order_color[3][1], height=barSize, align='center')
      ax1.barh(i - offset, ntDataA[2], left=amDataA[2]+midDataA[2]+pmDataA[2]+evDataA[2], color=time_order_color[4][1], height=barSize, align='center')

      if amDataA[2]+midDataA[2]+pmDataA[2]+evDataA[2]+ntDataA[2] > maxPositiveStopTotal:
         maxPositiveStopTotal = amDataA[2]+midDataA[2]+pmDataA[2]+evDataA[2]+ntDataA[2]


    # OUTBOUOND Data
    # Set the y-ticks to the keys in the dictionary
    stopIds = list(outbound_after.keys())
    stopNames = []
    for i in range(len(stopIds)):
      stopNames.append(stopDataAM.getStopNameForStopId(stopIds[i]))

    ax2.set_yticks(range(len(stopNames)))
    ax2.set_yticklabels(stopNames)

    firstDot = True
    # Iterate over each key in the data dictionary
    for i, stopId in enumerate(stopIds):
      if firstDot:
        firstDot = False
        for t_o_color in time_order_color:
          ax2.barh(i, 5, color=t_o_color[1], label=f'{beforeMonth} {t_o_color[0]}', left=5000, alpha=0.5)
          ax2.barh(i, 5, color=t_o_color[1], label=f'{afterMonth} {t_o_color[0]}', left=5000)


      before_values = []
      after_values = []

      # Fix renamed stops manually for now.
      if stopId == "3267":
        # Swift Blue did not stop at Shoreline north before, so all data is zero
        before_values = [[0 for _ in range(3)] for _ in range(5)]
      else:
        before_values = outbound_before[stopId]
      after_values = outbound_after[stopId]

      printStopValues(stopId, before_values, after_values, "outbound", stopDataAM)
    

      # before values: [[ridership, alights, boards],[ridership, alights, boards],..]
      amDataB = before_values[0]
      midDataB = before_values[1]
      pmDataB = before_values[2]
      evDataB = before_values[3]
      ntDataB = before_values[4]
      # Inbound alights before
      ax2.barh(i + offset, -amDataB[1], color=time_order_color[0][1], height=barSize, align='center', alpha=0.5)
      ax2.barh(i + offset, -midDataB[1], left=-amDataB[1], color=time_order_color[1][1], height=barSize, align='center', alpha=0.5)
      ax2.barh(i + offset, -pmDataB[1], left=-amDataB[1]-midDataB[1], color=time_order_color[2][1], height=barSize, align='center', alpha=0.5)
      ax2.barh(i + offset, -evDataB[1], left=-amDataB[1]-midDataB[1]-pmDataB[1], color=time_order_color[3][1], height=barSize, align='center', alpha=0.5)
      ax2.barh(i + offset, -ntDataB[1], left=-amDataB[1]-midDataB[1]-pmDataB[1]-evDataB[1], color=time_order_color[4][1], height=barSize, align='center', alpha=0.5)
      if amDataB[1]+midDataB[1]+pmDataB[1]+evDataB[1]+ntDataB[1] > maxNegativeStopTotal:
         maxNegativeStopTotal = amDataB[1]+midDataB[1]+pmDataB[1]+evDataB[1]+ntDataB[1]

      # after values: [[ridership, alights, boards],[ridership, alights, boards],..]
      amDataA = after_values[0]
      midDataA = after_values[1]
      pmDataA = after_values[2]
      evDataA = after_values[3]
      ntDataA = after_values[4]
      # Inbound alights after
      ax2.barh(i - offset, -amDataA[1], color=time_order_color[0][1], height=barSize, align='center')
      ax2.barh(i - offset, -midDataA[1], left=-amDataA[1], color=time_order_color[1][1], height=barSize, align='center')
      ax2.barh(i - offset, -pmDataA[1], left=-amDataA[1]-midDataA[1], color=time_order_color[2][1], height=barSize, align='center')
      ax2.barh(i - offset, -evDataA[1], left=-amDataA[1]-midDataA[1]-pmDataA[1], color=time_order_color[3][1], height=barSize, align='center')
      ax2.barh(i - offset, -ntDataA[1], left=-amDataA[1]-midDataA[1]-pmDataA[1]-evDataA[1], color=time_order_color[4][1], height=barSize, align='center')
      if amDataA[1]+midDataA[1]+pmDataA[1]+evDataA[1]+ntDataA[1] > maxNegativeStopTotal:
         maxNegativeStopTotal = amDataA[1]+midDataA[1]+pmDataA[1]+evDataA[1]+ntDataA[1]


      # Inbound boardings before
      ax2.barh(i + offset, amDataB[2], color=time_order_color[0][1], height=barSize, align='center', alpha=0.5)
      ax2.barh(i + offset, midDataB[2], left=amDataB[2], color=time_order_color[1][1], height=barSize, align='center', alpha=0.5)
      ax2.barh(i + offset, pmDataB[2], left=amDataB[2]+midDataB[2], color=time_order_color[2][1], height=barSize, align='center', alpha=0.5)
      ax2.barh(i + offset, evDataB[2], left=amDataB[2]+midDataB[2]+pmDataB[2], color=time_order_color[3][1], height=barSize, align='center', alpha=0.5)
      ax2.barh(i + offset, ntDataB[2], left=amDataB[2]+midDataB[2]+pmDataB[2]+evDataB[2], color=time_order_color[4][1], height=barSize, align='center', alpha=0.5)

      if amDataB[2]+midDataB[2]+pmDataB[2]+evDataB[2]+ntDataB[2] > maxPositiveStopTotal:
         maxPositiveStopTotal = amDataB[2]+midDataB[2]+pmDataB[2]+evDataB[2]+ntDataB[2]


       # Inbound boardings after
      ax2.barh(i - offset, amDataA[2], color=time_order_color[0][1], height=barSize, align='center')
      ax2.barh(i - offset, midDataA[2], left=amDataA[2], color=time_order_color[1][1], height=barSize, align='center')
      ax2.barh(i - offset, pmDataA[2], left=amDataA[2]+midDataA[2], color=time_order_color[2][1], height=barSize, align='center')
      ax2.barh(i - offset, evDataA[2], left=amDataA[2]+midDataA[2]+pmDataA[2], color=time_order_color[3][1], height=barSize, align='center')
      ax2.barh(i - offset, ntDataA[2], left=amDataA[2]+midDataA[2]+pmDataA[2]+evDataA[2], color=time_order_color[4][1], height=barSize, align='center')

      if amDataA[2]+midDataA[2]+pmDataA[2]+evDataA[2]+ntDataA[2] > maxPositiveStopTotal:
         maxPositiveStopTotal = amDataA[2]+midDataA[2]+pmDataA[2]+evDataA[2]+ntDataA[2]




    print(maxNegativeStopTotal)
    print(maxPositiveStopTotal)
    lowerLimit = (maxNegativeStopTotal + 0.1 * maxNegativeStopTotal) * -1
    upperLimit = maxPositiveStopTotal + 0.1 * maxPositiveStopTotal
    ax1.set_xlim(lowerLimit, upperLimit)  # Set x-axis limits
    ax2.set_xlim(lowerLimit, upperLimit) # Set x-axis limits
    ax1.legend(fontsize=legendTextSize)
    ax2.legend(fontsize=legendTextSize)
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # This reserves space for the suptitle

    plt.subplots_adjust(top=0.92)

    # eg: src/graphs/kcm/7/24/241/Weekday/TripRidership.png
    directory = f"../../graphs/{constants.agencyIdAndInitials[afterRouteDataAM.routeSettings.agencyId]}/{afterRouteDataAM.routeSettings.routeNum}"
    os.makedirs(directory, exist_ok=True)
    output_file = os.path.join(directory, 'BeforeAfterRidership.png')
    fig.savefig(output_file)   # save the plot to file

def plot_link_data(routeDataAM:RouteDataAccessModule):
    inbound_data = []
    outbound_data = []

    with open(routeDataAM.ridershipDatafilePath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                direction = row["Direction, Friendly"].strip()
                stop_name = row["LongName"].strip()
                station_code = int(row["stationCode"])
                boarding = int(row["BoardingCnt"])
                alighting = int(row["AlightingCnt"])
            except (ValueError, KeyError):
                continue  # skip rows with missing/invalid data

            stop_data = {
                "stop": stop_name,
                "station_code": station_code,
                "boarding": boarding,
                "alighting": alighting
            }

            if direction == "East" or direction == "South":
                inbound_data.append(stop_data)
            elif direction == "West" or direction == "North":
                outbound_data.append(stop_data)

    # Sort by station_code descending
    inbound_data.sort(key=lambda x: x["station_code"], reverse=True)
    outbound_data.sort(key=lambda x: x["station_code"], reverse=True)

    # Extract data for plotting

    #routeName = "Route {0}".format(routeDataAM.routeSettings.routeNum)
    routeName = routeDataAM.routeSettings.routeNum
    overallTitle = "Average Monthly Stop Ridership for the {0} in {1} 20{2}".format(routeName, calendar.month_name[int(routeDataAM.routeSettings.servicePeriod)], routeDataAM.routeSettings.year)
    inboundTitle = "Inbound Trips"
    outboundTitle = "Outbound Trips"
    inboundYAxis = "{0} Inbound Stops (Read Down)".format(routeName)
    outboundYAxis = "{0} Outbound Stops (Read Up)".format(routeName)
    xAxis = "Passenger Count"

    mainTitleSize = 40
    subTitleSize = 30
    axisLabelSizeValue = min(getAxisLabelSize(len(inbound_data), len(outbound_data)), 20)
    axisLabelSize = axisLabelSizeValue 
    axisIncrementsSize = axisLabelSizeValue
    legendTextSize = 15
    barSize = 0.6

    
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(30, 20))
    plt.rc('xtick', labelsize=12)     
    plt.rc('ytick', labelsize=12)
    ax1.set_xlabel(xAxis, fontsize=axisLabelSize)
    ax1.set_ylabel(inboundYAxis, fontsize=axisLabelSize)
    ax1.set_title(inboundTitle, fontsize=subTitleSize)
    ax1.tick_params(axis='x', labelsize=axisIncrementsSize)
    ax1.tick_params(axis='y', labelsize=axisIncrementsSize)

    ax2.set_xlabel(xAxis, fontsize=axisLabelSize)
    ax2.set_ylabel(outboundYAxis, fontsize=axisLabelSize)
    ax2.set_title(outboundTitle, fontsize=subTitleSize)
    ax2.tick_params(axis='x', labelsize=axisIncrementsSize)
    ax2.tick_params(axis='y', labelsize=axisIncrementsSize)
    
    fig.suptitle(overallTitle, fontsize=mainTitleSize)

    ax1.grid(True)
    ax2.grid(True)
    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)

    # Use union of stop names from both east and west, matched by station code
    station_code_to_name = {}
    for entry in inbound_data + outbound_data:
        station_code_to_name[entry["station_code"]] = entry["stop"]

    # Get all unique station codes sorted descending
    all_station_codes = sorted(set(station_code_to_name.keys()), reverse=True)
    print(all_station_codes)
    stop_labels = [station_code_to_name[code] for code in all_station_codes]
    print(stop_labels)
    ax1.set_yticks(range(len(stop_labels)))
    ax1.set_yticklabels(stop_labels)
    ax2.set_yticks(range(len(stop_labels)))
    ax2.set_yticklabels(stop_labels)

    barSize = 0.6


    for i, entry in enumerate(inbound_data):
        ax1.barh(i, -entry["alighting"], color=to_rgba("orange", 0.5), height=barSize, label="Alightings" if i == 0 else "")
        ax1.barh(i, entry["boarding"], color="orange", height=barSize, label="Boardings" if i == 0 else "")

    ax1.legend()

    for i, entry in enumerate(outbound_data):
        ax2.barh(i, -entry["alighting"], color=to_rgba("blue", 0.5), height=barSize, label="Alightings" if i == 0 else "")
        ax2.barh(i, entry["boarding"], color="blue", height=barSize, label="Boardings" if i == 0 else "")

    ax2.legend()

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    #plt.show()
    directory = f"../../graphs/{constants.agencyIdAndInitials[routeDataAM.routeSettings.agencyId]}/{routeDataAM.routeSettings.routeNum}/{routeDataAM.routeSettings.year}/{routeDataAM.routeSettings.servicePeriod}/{routeDataAM.routeSettings.dayType}"
    os.makedirs(directory, exist_ok=True)
    output_file = os.path.join(directory, 'monthlyRidership.png')
    fig.savefig(output_file)   # save the plot to file

def plot_link_data_may_2025(routeName):
  directionA = ""
  directionB = ""
  data = []
  dataPath = ""
  shortName = ""
  plotColor = ""

  if routeName == "1 Line":
    dataPath = "../../data/stRouteData/1 Line/25/5/Weekday/perDirectionLinkBoardings.csv"
    directionA = "South"
    directionB = "North"
    shortName = "1Line"
    plotColor = "#5caa42"
  if routeName == "2 Line":
    dataPath = "../../data/stRouteData/2 Line/25/5/Weekday/perDirectionLinkBoardings.csv"
    directionA = "West"
    directionB = "East"
    shortName = "2Line"
    plotColor = "#449fda"

  with open(dataPath, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            stop_name = row["Station"].strip()
            aBoarding = int(row[directionA])
            bBoarding = int(row[directionB])
            station_code = int(row["stationCode"])
        except (ValueError, KeyError):
            continue  # skip rows with missing/invalid data

        stop_data = {
            "stop": stop_name,
            "aBoarding": aBoarding,
            "bBoarding": bBoarding,
            "stopCode": station_code
        }

        data.append(stop_data)

  if routeName == "1 Line":
    data.sort(key=lambda x: x["stopCode"], reverse=True)
  if routeName == "2 Line":
    data.sort(key=lambda x: x["stopCode"])


  routeName = routeName
  overallTitle = "Average Weekday Boardings by Station for the {0} in May 2025".format(routeName)
  yAxis = "{0} Stations".format(routeName)
  xAxis = "Passenger Count"

  mainTitleSize = 40
  subTitleSize = 30
  axisLabelSizeValue = min(getAxisLabelSize(len(data), 0), 20)
  axisLabelSize = axisLabelSizeValue 
  axisIncrementsSize = axisLabelSizeValue
  legendTextSize = 20
  barSize = 0.6

  fig, ax1 = plt.subplots(nrows=1, ncols=1, figsize=(30, 20))
  plt.rc('xtick', labelsize=12)     
  plt.rc('ytick', labelsize=12)
  ax1.set_xlabel(xAxis, fontsize=axisLabelSize)
  ax1.set_ylabel(yAxis, fontsize=axisLabelSize)
  ax1.tick_params(axis='x', labelsize=axisIncrementsSize)
  ax1.tick_params(axis='y', labelsize=axisIncrementsSize)
  ax1.grid(True)
  ax1.set_axisbelow(True)


  fig.suptitle(overallTitle, fontsize=mainTitleSize)

  station_code_to_name = {}
  for entry in data:
      station_code_to_name[entry["stopCode"]] = entry["stop"]

  # Get all unique station codes sorted descending
  all_station_codes = []

  if routeName == "1 Line":
    all_station_codes = sorted(set(station_code_to_name.keys()), reverse=True)
  if routeName == "2 Line":
    all_station_codes = sorted(set(station_code_to_name.keys()))
  
  stop_labels = [station_code_to_name[code] for code in all_station_codes]
  print(stop_labels)
  ax1.set_yticks(range(len(stop_labels)))
  ax1.set_yticklabels(stop_labels)

  barSize = 0.6

  for i, entry in enumerate(data):
      ax1.barh(i, -entry["aBoarding"], color=to_rgba(plotColor, 0.5), height=barSize, label=f"{directionA}bound Boardings" if i == 0 else "")
      ax1.barh(i, entry["bBoarding"], color=plotColor, height=barSize, label=f"{directionB}bound Boardings" if i == 0 else "")

  ax1.legend(fontsize=legendTextSize)

  plt.tight_layout(rect=[0, 0, 1, 0.95])
  # plt.show()
  directory = f"../../graphs/st/{routeName}"
  os.makedirs(directory, exist_ok=True)
  output_file = os.path.join(directory, f'average{shortName}WeekdayBoardingsByDirection.png')
  fig.savefig(output_file)   # save the plot to file
