import re


def split_data_by_direction(data):
    # Initialize two dictionaries for 'I' and 'O' directions
    direction_I = {}
    direction_O = {}

    # Define the order of times
    time_order = ['AM', 'MID', 'PM', 'XEV', 'XNT']

    # Iterate through the original dictionary
    for key, value in data.items():
        direction = key[0]  # First character (either 'I' or 'O')
        
        # Extract stop ID and time using regex
        match = re.match(r'([IO])(\d+)([A-Z]+)', key)
        if not match:
            continue  # Skip if the key format is unexpected
        
        stop_id = match.group(2)  # Extract numeric stop ID
        time = match.group(3)  # Extract time part

        # Determine which dictionary to add the data to
        if direction == 'I':
            if stop_id not in direction_I:
                direction_I[stop_id] = [-1] * len(time_order)  # Initialize with -1s
            if time in time_order:
                direction_I[stop_id][time_order.index(time)] = float(value)
        elif direction == 'O':
            if stop_id not in direction_O:
                direction_O[stop_id] = [-1] * len(time_order)  # Initialize with -1s
            if time in time_order:
                direction_O[stop_id][time_order.index(time)] = float(value)

    return direction_I, direction_O

def combine_dictionaries(dict1, dict2, dict3):
    # Initialize the combined dictionary
    combined_dict = {}

    # Iterate through the keys in one of the dictionaries (since all have identical keys)
    for key in dict1.keys():
        # Initialize the nested list for the current key
        combined_values = []
        
        # Iterate over the indices (0 to 4) to create the list of 3 values for each index
        for i in range(len(dict1[key])):
            combined_values.append([dict1[key][i], dict2[key][i], dict3[key][i]])
        
        # Assign the nested list to the key in the combined dictionary
        combined_dict[key] = combined_values

    return combined_dict

# Input data is in the form: {'12485': [11.733, 26.6, 20.467, 12.2, 9.233], '8440': [11.467, 10.7, 7.533, 2.667, 1.733] .... }
def get_total_board_alight_per_stop(alightData, boardingData):
    cumulative_alighting_dict = {}
    cumulative_boarding_dict = {}
    cumulative_per_stop_dict = {}
    # First, add up the values for all time periods:
    for key in alightData.keys():
      cumulative_alighting_dict[key] = round(alightData[key][0] + alightData[key][1] + alightData[key][2] + alightData[key][3] + alightData[key][4], 2)
    for key in boardingData.keys():
      cumulative_boarding_dict[key] = round(boardingData[key][0] + boardingData[key][1] + boardingData[key][2] + boardingData[key][3] + boardingData[key][4], 2)

    for key in alightData.keys():
        cumulative_per_stop_dict[key] = (cumulative_alighting_dict[key], cumulative_boarding_dict[key])
    return cumulative_per_stop_dict

# per stop dict in the format: {'31137': (0.13, 231.6), '31136': (5.77, 141.0), '30122': (7.87, 53.13),...}
def get_ridership_between_stops(cumulative_per_stop_dict, startStop, endStop):
    total_passengers = 0
    
    # Calculate passengers already on the bus before start_stop
    for stop in range(1, startStop):
        alight, board = cumulative_per_stop_dict[stop]
        total_passengers += (board - alight)
    
    # Add the passengers between start_stop and end_stop
    for stop in range(startStop, endStop + 1):
        alight, board = cumulative_per_stop_dict[stop]
        total_passengers += (board - alight)
    
    return total_passengers

  


def reorder_dict_with_prefix(keys_order, combined_dict):
    # Create a new dictionary with keys ordered as in keys_order
    ordered_dict = {}
    for key in keys_order:
        # Strip prefix (anything before "_") to get the actual key
        if key in combined_dict:
            ordered_dict[key] = combined_dict[key]
    return ordered_dict

def cumulative_dict(input_dict):
    # Initialize the cumulative dictionary
    cumulative_dict = {}
    
    # Initialize a list to hold the running cumulative sum
    cumulative_sum = [0] * len(next(iter(input_dict.values())))
    
    for key, values in input_dict.items():
        # Update cumulative sum with the current list of values
        cumulative_sum = [cumulative_sum[i] + values[i] for i in range(len(values))]
        
        # Assign the updated cumulative sum to the corresponding key in the new dictionary
        cumulative_dict[key] = cumulative_sum.copy()
    
    return cumulative_dict