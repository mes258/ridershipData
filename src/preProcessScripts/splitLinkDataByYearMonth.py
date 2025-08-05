# Csv has columns: 
#DateValue - Year	DateValue - Month	Direction, Friendly	LongName	Line_Temp	BoardingCnt	AlightingCnt
#2023	July	North	Northgate	1 Line	7227	112318
#2023	August	North	Northgate	1 Line	4521	74806
import sys

import os
import csv
import calendar
sys.path.insert(0, "../../src")

from util import constants

# Replace with the actual file path
input_file = '../../data/rawData/st/2023-2025LinkData.csv'  

def month_name_to_number(month_name):
    month_name = month_name.capitalize()  # Ensure the first letter is capitalized
    month_number = list(calendar.month_name).index(month_name)
    return month_number
    
# Open the input CSV file
with open(input_file, mode='r', newline='') as infile:
    reader = csv.DictReader(infile)

    for row in reader:
        # Extract SERVICE_CHANGE_NUM and SERVICE_RTE_NUM values
        year = row['DateValue - Year']
        month = month_name_to_number(row['DateValue - Month'])
        service_rte_num = row['Line_Temp']
        row["stationCode"] = constants.linkStationIdNumbers[row['LongName']]
        
        # Create the directory path based on SERVICE_CHANGE_NUM and SERVICE_RTE_NUM
        # eg: 7/24/241
        directory = f"../../data/stRouteData/{service_rte_num}/{year[2:]}/{month}/Weekday"
        os.makedirs(directory, exist_ok=True)
        
        # Define the output file path
        output_file = os.path.join(directory, 'stopLevelData.csv')
        
        # Check if the file already exists to determine whether to write the header
        file_exists = os.path.isfile(output_file)
        
        # Write the row to the appropriate stopLevelData.csv file
        with open(output_file, mode='a', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            if not file_exists:
                writer.writeheader()  # Write the header if the file does not exist
            writer.writerow(row)