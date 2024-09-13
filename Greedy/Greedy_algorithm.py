import pandas as pd
import os

# Define base directories for inputs and outputs
input_base_dir = 'Greedy/input'
output_base_dir = 'Greedy/output'
instance_numbers = ['01', '02', '03']  # Define the instances

# Function to run the Greedy Assignment Algorithm
def greedy_assignment(instance_number, service_times_file, estimated_profits_file, delivery_costs_file, workers_file, orders_file):
    # Load the service times, estimated profits, delivery costs, workers, and orders data
    service_times_df = pd.read_csv(service_times_file)
    estimated_profits_df = pd.read_csv(estimated_profits_file)
    delivery_costs_df = pd.read_csv(delivery_costs_file)
    workers_df = pd.read_csv(workers_file)
    orders_df = pd.read_csv(orders_file)

    # Combine the metrics into a single DataFrame for easy processing
    combined_df = service_times_df.merge(estimated_profits_df, on=['order_id', 'worker_id']).merge(delivery_costs_df, on=['order_id', 'worker_id'])

    # Standardize worker locations
    workers_df['current_location'] = workers_df['current_location'].str.strip().str.upper()

    # Initialize assignment dictionary
    assignments = []

    assigned_workers = set()  # To keep track of workers that have already been assigned

    # Process each order
    for _, order in orders_df.iterrows():
        order_id = order['order_id']

        # Filter to get only the relevant rows for this order
        relevant_rows = combined_df[combined_df['order_id'] == order_id]

        best_worker = None
        best_distance = float('inf')

        # Find the best (closest) worker for this order
        for _, row in relevant_rows.iterrows():
            worker_id = row['worker_id']

            if worker_id not in assigned_workers:  # Ensure this worker hasn't been assigned yet
                distance = row['service_time']  # Using service time as a proxy for distance/effort

                if distance < best_distance:
                    best_distance = distance
                    best_worker = worker_id

        # Assign the closest worker to the order
        if best_worker is not None:
            assignments.append({
                'order_id': order_id,
                'worker_id': best_worker,
                'service_time': best_distance,
                'delivery_cost': relevant_rows.loc[relevant_rows['worker_id'] == best_worker, 'delivery_cost'].values[0],
                'estimated_profit': relevant_rows.loc[relevant_rows['worker_id'] == best_worker, 'estimated_profit'].values[0]
            })

            assigned_workers.add(best_worker)  # Mark this worker as assigned

    # Convert assignments to DataFrame for output
    assignments_df = pd.DataFrame(assignments)

    # Save the results to a CSV file in the output folder for this instance
    output_dir = os.path.join(output_base_dir, f'instance-{instance_number}')
    os.makedirs(output_dir, exist_ok=True)  # Create the output directory if it doesn't exist
    output_file = os.path.join(output_dir, f'greedy_assignments_{instance_number}.csv')
    assignments_df.to_csv(output_file, index=False)

    print(f"Greedy assignments for instance {instance_number} saved to {output_file}")
    return assignments_df

# Loop over each instance and run the greedy assignment process
for instance_number in instance_numbers:
    print(f"Processing instance {instance_number} with Greedy Assignment...")

    # Define file paths for the current instance
    instance_input_dir = os.path.join(input_base_dir, f'instance-{instance_number}')
    service_times_file = os.path.join(instance_input_dir, f'service-times-{instance_number}.csv')
    estimated_profits_file = os.path.join(instance_input_dir, f'estimated-profits-{instance_number}.csv')
    delivery_costs_file = os.path.join(instance_input_dir, f'delivery-costs-{instance_number}.csv')
    workers_file = os.path.join(instance_input_dir, f'workers-{instance_number}.csv')
    orders_file = os.path.join(instance_input_dir, f'orders-{instance_number}.csv')

    # Run the greedy assignment method for this instance
    greedy_assignment(instance_number, service_times_file, estimated_profits_file, delivery_costs_file, workers_file, orders_file)
