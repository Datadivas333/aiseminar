import pandas as pd
import numpy as np
import os
from datetime import datetime, timezone
from math import radians, sin, cos, sqrt, atan2

def calculate_waiting_time(fetch_time, ready_time):
    # Convert both fetch_time and ready_time to datetime objects
    fetch_time_dt = datetime.fromtimestamp(fetch_time, timezone.utc)
    ready_time_dt = datetime.fromtimestamp(ready_time, timezone.utc)

    # If fetch_time is less than or equal to ready_time, waiting time is 0
    if fetch_time_dt <= ready_time_dt:
        return 0
    
    # Otherwise, calculate the waiting time in minutes
    waiting_time_seconds = (fetch_time_dt - ready_time_dt).total_seconds()
    return waiting_time_seconds / 60  # Convert seconds to minutes

def scale_coordinates(value, scale_factor=1e6):
    # Assuming the input data is scaled and needs to be reduced to a meaningful value
    return value / scale_factor

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of the Earth in kilometers
    # Convert latitude and longitude from degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Compute differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    
    return distance

def algorithm_1(folder_path, instance_num):
    # Construct the file paths based on the instance number
    orders_file = os.path.join(folder_path, f'orders-{instance_num}.csv').replace("\\", "/")
    workers_file = os.path.join(folder_path, f'workers-{instance_num}.csv').replace("\\", "/")
    locations_file = os.path.join(folder_path, f'locations-{instance_num}.csv').replace("\\", "/")
    instance_params_file = os.path.join(folder_path, f'parameters-{instance_num}.csv').replace("\\", "/")

    # Check if all the files exist before proceeding
    for file_path in [orders_file, workers_file, locations_file, instance_params_file]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

    # Load data from CSV files
    orders = pd.read_csv(orders_file)
    workers = pd.read_csv(workers_file)
    locations = pd.read_csv(locations_file)
    instance_params = pd.read_csv(instance_params_file)

    # Calculate waiting_time based on fetch_time and ready_time
    orders['waiting_time'] = orders.apply(lambda row: calculate_waiting_time(row['fetch_time'], row['ready_time']), axis=1)

    # Standardize location IDs (strip whitespace, convert to uppercase)
    locations['location_id'] = locations['location_id'].str.strip().str.upper()
    orders['pickup_location'] = orders['pickup_location'].str.strip().str.upper()
    orders['delivery_location'] = orders['delivery_location'].str.strip().str.upper()
    workers['current_location'] = workers['current_location'].str.strip().str.upper()

    # Scale coordinates (assuming they need to be scaled down for calculation)
    locations['x'] = locations['x'].apply(scale_coordinates)
    locations['y'] = locations['y'].apply(scale_coordinates)

    # Extract parameters from the instance parameters file
    mu = instance_params.loc[0, 'mu']
    m_ow = instance_params.loc[0, 'm_ow']
    speed = instance_params.loc[0, 'speed']

    # Initialize output dictionaries
    service_times = {}
    delivery_costs = {}
    estimated_profits = {}

    # Iterate over each order and worker pair
    for _, order in orders.iterrows():
        order_id = order['order_id']
        pickup_location = order['pickup_location']
        delivery_location = order['delivery_location']

        for _, worker in workers.iterrows():
            worker_id = worker['worker_id']
            worker_location = worker['current_location']

            try:
                # Extract coordinates
                worker_coords = locations.loc[locations['location_id'] == worker_location, ['x', 'y']].values[0]
                pickup_coords = locations.loc[locations['location_id'] == pickup_location, ['x', 'y']].values[0]
                delivery_coords = locations.loc[locations['location_id'] == delivery_location, ['x', 'y']].values[0]

                # Calculate distances using the Haversine formula
                d_p = haversine(worker_coords[1], worker_coords[0], pickup_coords[1], pickup_coords[0])
                d_d = haversine(pickup_coords[1], pickup_coords[0], delivery_coords[1], delivery_coords[0])

                # Calculate times (using the speed parameter to determine travel time)
                t_p = (d_p / speed) * 60  # Convert hours to minutes
                t_w = order['waiting_time']  # This is now in minutes
                t_d = (d_d / speed) * 60  # Convert hours to minutes

                # Calculate service time
                s_ow = t_p + t_w + t_d
                service_times[(order_id, worker_id)] = s_ow

                # Calculate delivery cost
                c_ow = mu * (d_p + d_d)
                delivery_costs[(order_id, worker_id)] = c_ow

                # Calculate estimated profit
                p_ow = m_ow - c_ow
                estimated_profits[(order_id, worker_id)] = p_ow

            except KeyError as e:
                print(f"Error processing order {order_id} and worker {worker_id}: {e}")

    # Convert dictionaries to DataFrames for easier use in subsequent algorithms
    service_times_df = pd.DataFrame.from_dict(service_times, orient='index', columns=['service_time'])
    delivery_costs_df = pd.DataFrame.from_dict(delivery_costs, orient='index', columns=['delivery_cost'])
    estimated_profits_df = pd.DataFrame.from_dict(estimated_profits, orient='index', columns=['estimated_profit'])

    # Convert the tuple index into two separate columns: order_id and worker_id for all DataFrames
    for df in [service_times_df, delivery_costs_df, estimated_profits_df]:
        df['order_id'] = df.index.map(lambda x: x[0])
        df['worker_id'] = df.index.map(lambda x: x[1])

    # Round the numeric values to 5 decimal places for all DataFrames
    service_times_df['service_time'] = service_times_df['service_time'].round(5)
    delivery_costs_df['delivery_cost'] = delivery_costs_df['delivery_cost'].round(5)
    estimated_profits_df['estimated_profit'] = estimated_profits_df['estimated_profit'].round(5)

    # Reorder the columns to match the desired output format
    service_times_df = service_times_df[['order_id', 'worker_id', 'service_time']]
    delivery_costs_df = delivery_costs_df[['order_id', 'worker_id', 'delivery_cost']]
    estimated_profits_df = estimated_profits_df[['order_id', 'worker_id', 'estimated_profit']]

    return service_times_df, delivery_costs_df, estimated_profits_df

# Define the input directories and corresponding instance numbers
input_folders = ['alg1-inputs/instance-01', 'alg1-inputs/instance-02', 'alg1-inputs/instance-03']
instance_numbers = ['01', '02', '03']

# Iterate over each input folder and run the algorithm for each instance
for folder, instance_num in zip(input_folders, instance_numbers):
    # Run the algorithm for the current instance
    try:
        service_times_df, delivery_costs_df, estimated_profits_df = algorithm_1(folder, instance_num)

        # Define the output directory for the current instance
        output_dir = f'{folder.replace("inputs", "outputs")}'

        # Check if the directory exists, and create it if it doesn't
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save the outputs to CSV files in the specified folder
        service_times_df.to_csv(os.path.join(output_dir, f'service-times-{instance_num}.csv'), index=False)
        delivery_costs_df.to_csv(os.path.join(output_dir, f'delivery-costs-{instance_num}.csv'), index=False)
        estimated_profits_df.to_csv(os.path.join(output_dir, f'estimated-profits-{instance_num}.csv'), index=False)

        print(f"Instance {instance_num} processed and results saved to {output_dir}.")

    except FileNotFoundError as e:
        print(e)
