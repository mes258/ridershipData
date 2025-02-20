import matplotlib.pyplot as plt
from accessModules import routeDataAccessModule
from accessModules import stopDataAccessModule
import matplotlib.patches as mpatches
import numpy as np

#AM - 5AM-9AM, MID - 9AM-3PM, PM - 3PM-7PM, XEV - 7PM - 10PM, XNT 10PM - 5AM
time_order_color = [['5am-9am (AM)', 'y'], ['9am-3pm (MID)', 'b'], ['3pm-7pm (PM)', 'g'], ['7pm-10pm (XEV)', 'm'], ['10pm-5am (XNT)', 'k']]

def plot_multiple_lines_with_deviation(sorted_data, am, xAxisName, yAxisName, title):   
    print(sorted_data) 
    # Extract the keys (intervals) for the x-axis
    x = list(sorted_data.keys())
    for i in range(len(x)):
        try:
          x[i] = stopDataAccessModule.getStopNameFromStopId(am.routeNum, x[i])
        except:
          x[i] = am.getStopNameFromStopId(x[i])
    
    # Assume all lists have the same length and initialize y values lists
    num_lines = len(next(iter(sorted_data.values())))
    y_values = [[] for _ in range(num_lines)]
    y_upper_deviation = [[] for _ in range(num_lines)]
    y_lower_deviation = [[] for _ in range(num_lines)]

    # Populate y_values with corresponding values for each line
    for key, values in sorted_data.items():
        for i in range(num_lines):
            y_values[i].append(float(values[i][0]))
            y_lower_deviation[i].append(float(values[i][1]))
            y_upper_deviation[i].append(float(values[i][2]))
    
    # Plot each line
    plt.figure(figsize=(8, 8))
    plt.rc('xtick', labelsize=8)     
    plt.rc('ytick', labelsize=8)

    for i in range(num_lines):
        y_err = [y_lower_deviation[i], y_upper_deviation[i]]
        plt.errorbar(y_values[i], x, xerr=y_err, fmt='o' + time_order_color[i][1], ecolor=time_order_color[i][1], capsize=5, label=time_order_color[i][0])
        #plt.errorbar(y_values[i], x, xerr=y_err, fmt='o' + time_order_color[i][1], ecolor=time_order_color[i][1], capsize=5, label=time_order_color[i][0])

    # Add labels and title
    plt.xlabel(xAxisName)
    plt.ylabel(yAxisName)
    plt.title(title)
    plt.xlim(left=0)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=0, ha="center")
    
    boardingText = "+ Error Bar: Avg Boardings"
    plt.scatter([], [], color="w", alpha=1, label=boardingText)

    alightingText = "- Error Bar: Avg Alightings"
    plt.scatter([], [], color="w", alpha=1, label=alightingText)

    handles, labels = plt.gca().get_legend_handles_labels()
    order = [2,3,4,5,6,0,1]
    plt.legend([handles[idx] for idx in order],[labels[idx] for idx in order])
    # Add legend
    #plt.legend()
    
    # Show grid
    plt.grid(True)
    
    # Display the plot
    plt.tight_layout()
    plt.show()

def plot_data_multiple_lines(sorted_data, am, xAxisName, yAxisName, title):
    # Extract the keys (intervals) for the x-axis
    x = list(sorted_data.keys())
    for i in range(len(x)):
        try:
          x[i] = stopDataAccessModule.getStopNameFromStopId(am.routeNum, x[i])
        except:
          x[i] = am.getStopNameFromStopId(x[i])
    
    # Assume all lists have the same length and initialize y values lists
    num_lines = len(next(iter(sorted_data.values())))
    y_values = [[] for _ in range(num_lines)]

    # Populate y_values with corresponding values for each line
    for key, values in sorted_data.items():
        for i in range(num_lines):
            y_values[i].append(float(values[i]))
    
    # Plot each line
    plt.figure(figsize=(12, 8))

    for i in range(num_lines):
        plt.plot(x, y_values[i], 'o' + time_order_color[i][1], linestyle='None', label=time_order_color[i][0])

    # Add labels and title
    plt.xlabel(xAxisName)
    plt.ylabel(yAxisName)
    plt.title(title)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=90)
    
    # Add legend
    plt.legend()
    
    # Show grid
    plt.grid(True)
    
    # Display the plot
    plt.tight_layout()
    plt.show()


def plot_boarding_bars_and_dot_ridership(inbound_sorted_data, outbound_sorted_data, am: accessModule.AccessModule, perHour: bool):
    # Before setting up the plot, create all the labels: 
    routeName = "Route {0}".format(am.routeNum)
    for letter, rapidRideRouteNum, shortName in stopDataAccessModule.rapidRideMappings:
      if am.routeNum == rapidRideRouteNum:
        routeName = shortName

    # At this point, route name is either "Route N" or "X Line"
    # Need Overall title, per chart title, per chart y axis label, x axis label
    overallTitle = "Average Weekday Ridership per {0} Trip in 20{1}".format(routeName, am.year)
    inboundTitle = "Inbound Trips"
    outboundTitle = "Outbound Trips"
    inboundYAxis = "{0} Inbound Stops (Read Down)".format(routeName)
    outboundYAxis = "{0} Outbound Stops (Read Up)".format(routeName)
    xAxis = "Passenger Count"

    if perHour:
      overallTitle = "{0} Boardings and Alightings per Hour".format(routeName)

    mainTitleSize = 40
    subTitleSize = 30
    axisLabelSize = 20 # change to 13 for route with a lot of stops (eg: 165)
    axisIncrementsSize = 20 # change to 13 for route with a lot of stops (eg: 165)
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
    if perHour:
      ax1.set_xlim(-60, 60) 
      ax2.set_xlim(-60, 60)
    
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
            
            if not perHour:
              # Plot dot for the first value (with slight vertical spacing for time periods)
              ax1.plot(dot, y_pos, 'o' + time_order_color[j][1], label=f'{time_order_color[j][0]}', markersize=7)

              # Plot negative bar for the second value and positive bar for the third value
              ax1.barh(y_pos, -neg_bar, color=time_order_color[j][1], height=0.15, align='center')
              ax1.barh(y_pos, pos_bar, color=time_order_color[j][1], height=0.15, align='center')
            else:
               # For per hour, divide the total by hour count
              ax1.barh(i, -neg_bar/time_order_color[j][2], color=time_order_color[j][1], height=0.15, align='center')
              ax1.barh(i, pos_bar/time_order_color[j][2], color=time_order_color[j][1], height=0.15, align='center')

    # Set the y-ticks to the keys in the dictionary
    x = list(inbound_sorted_data.keys())
    for i in range(len(x)):
        try:
          x[i] = stopDataAccessModule.getStopNameFromStopId(am.routeNum, x[i])
        except:
          x[i] = am.getStopNameFromStopId(x[i])


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
            
            if not perHour:
              # Plot dot for the first value (with slight vertical spacing for time periods)
              ax2.plot(dot, y_pos, 'o' + time_order_color[j][1], label=f'{time_order_color[j][0]}', markersize=7)

              # Plot negative bar for the second value and positive bar for the third value
              ax2.barh(y_pos, -neg_bar, color=time_order_color[j][1], height=0.15, align='center')
              ax2.barh(y_pos, pos_bar, color=time_order_color[j][1], height=0.15, align='center')
            else:
              ax2.barh(y_pos, -neg_bar/time_order_color[j][2], color=time_order_color[j][1], height=0.15, align='center')
              ax2.barh(y_pos, pos_bar/time_order_color[j][2], color=time_order_color[j][1], height=0.15, align='center')

    # Set the y-ticks to the keys in the dictionary
    x = list(outbound_sorted_data.keys())
    for i in range(len(x)):
        try:
          x[i] = stopDataAccessModule.getStopNameFromStopId(am.routeNum, x[i])
        except:
          x[i] = am.getStopNameFromStopId(x[i])


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
    if perHour:
      fig.savefig('{0}/{1}/{0}PerHourPlot.png'.format(am.routeNum, am.year))   # save the plot to file
    else:
      fig.savefig('{0}/{1}/{0}FullPlot.png'.format(am.routeNum, am.year))   # save the plot to file
    plt.close(fig)  


def plot_stacked_boarding_bars(inbound_sorted_data, outbound_sorted_data, am: accessModule.AccessModule):
   # Before setting up the plot, create all the labels: 
    routeName = "Route {0}".format(am.routeNum)
    for letter, rapidRideRouteNum, shortName in stopDataAccessModule.rapidRideMappings:
      if am.routeNum == rapidRideRouteNum:
        routeName = shortName

    # At this point, route name is either "Route N" or "X Line"
    # Need Overall title, per chart title, per chart y axis label, x axis label
    overallTitle = "Average Daily Stop Ridership for {0} in 20{1}".format(routeName, am.year)
    inboundTitle = "Inbound Trips"
    outboundTitle = "Outbound Trips"
    inboundYAxis = "{0} Inbound Stops (Read Down)".format(routeName)
    outboundYAxis = "{0} Outbound Stops (Read Up)".format(routeName)
    xAxis = "Passenger Count"

    mainTitleSize = 40
    subTitleSize = 30
    axisLabelSize = 20
    axisIncrementsSize = 20
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
        try:
          x[i] = stopDataAccessModule.getStopNameFromStopId(am.routeNum, x[i])
        except:
          x[i] = am.getStopNameFromStopId(x[i])


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
        try:
          x[i] = stopDataAccessModule.getStopNameFromStopId(am.routeNum, x[i])
        except:
          x[i] = am.getStopNameFromStopId(x[i])


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

    fig.savefig('{0}/{1}/{0}DailyTotals.png'.format(am.routeNum, am.year))   # save the plot to file
