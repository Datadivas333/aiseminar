import csv
import math
import os

# Function to scale coordinates from microdegrees to degrees
def scale_coordinates(value, scale_factor=1e6):
    return value / scale_factor

# Haversine formula to calculate the distance between two points on the Earth
def haversine(lon1, lat1, lon2, lat2):
    R = 6371  # Radius of Earth in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in kilometers

# Function to calculate the average speed
def calculate_average_speed(input_file, output_file):
    total_distance = 0
    total_time = 0
    count = 0

    # Open the file with utf-8-sig encoding to handle BOM
    with open(input_file, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Apply scaling to coordinates
            pick_up_lng = scale_coordinates(int(row['pick_up_lng']))
            pick_up_lat = scale_coordinates(int(row['pick_up_lat']))
            delivery_lng = scale_coordinates(int(row['delivery_lng']))
            delivery_lat = scale_coordinates(int(row['delivery_lat']))
            fetch_time = int(row['fetch_time'])
            arrive_time = int(row['arrive_time'])

            # Calculate distance between pickup and delivery points
            distance = haversine(pick_up_lng, pick_up_lat, delivery_lng, delivery_lat)

            # Calculate time duration in hours
            time_duration = (arrive_time - fetch_time) / 3600  # convert seconds to hours

            if time_duration > 0:  # Avoid division by zero
                total_distance += distance
                total_time += time_duration
                count += 1

    # Calculate average speed (kilometers per hour) and round to 2 decimal places
    average_speed = round(total_distance / total_time, 2) if total_time > 0 else 0

    # Write the result to the output file
    with open(output_file, mode='w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['average_speed_km_per_hour'])
        writer.writerow([average_speed])

# List of input files and their corresponding output files
input_files = [
    'average-speed-files/speed-input-01.csv',
    'average-speed-files/speed-input-02.csv',
    'average-speed-files/speed-input-03.csv'
]
output_files = [
    'average-speed-files/speed-01.csv',
    'average-speed-files/speed-02.csv',
    'average-speed-files/speed-03.csv'
]

# Iterate over each input and output file pair
for input_file, output_file in zip(input_files, output_files):
    calculate_average_speed(input_file, output_file)
    print(f"Processed {input_file}, results saved to {output_file}")
