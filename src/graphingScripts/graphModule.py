import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import OrderedDict
import os
import sys
sys.path.insert(0, "../../src")

from util import constants
from util import util
from ridershipPatternScripts.routeSettings import RouteSettings
from accessModules.routeDataAccessModule import RouteDataAccessModule
from accessModules.stopDataAccessModule import StopDataAccessModule


#AM - 5AM-9AM, MID - 9AM-3PM, PM - 3PM-7PM, XEV - 7PM - 10PM, XNT 10PM - 5AM
time_order_color = [['5am-9am (AM)', 'y'], ['9am-3pm (MID)', 'b'], ['3pm-7pm (PM)', 'g'], ['7pm-10pm (XEV)', 'm'], ['10pm-5am (XNT)', 'k']]

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
