import os
import csv

# Replace with the actual file path
input_file = '../../data/rawData/kcm/Fall_2024_Summarized_Stop_Data.csv'  

# Open the input CSV file
with open(input_file, mode='r', newline='') as infile:
    reader = csv.DictReader(infile)

    for row in reader:
        # Extract SERVICE_CHANGE_NUM and SERVICE_RTE_NUM values
        service_change_num = row['SERVICE_CHANGE_NUM']
        service_rte_num = row['SERVICE_RTE_NUM']
        
        # Create the directory path based on SERVICE_CHANGE_NUM and SERVICE_RTE_NUM
        # eg: 7/24/241
        directory = f"../../data/kcmRouteData/{service_rte_num}/{service_change_num[:2]}/{service_change_num}/Weekday"
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
