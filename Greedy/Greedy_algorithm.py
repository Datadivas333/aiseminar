import pandas as pd
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_dir}")

# Load the CSV files from the directory where the script is located
service_times_df = pd.read_csv(os.path.join(script_dir, 'service-times-01.csv'))
estimated_profits_df = pd.read_csv(os.path.join(script_dir, 'estimated-profits-01.csv'))
delivery_costs_df = pd.read_csv(os.path.join(script_dir, 'delivery-costs-01.csv'))
workers_df = pd.read_csv(os.path.join(script_dir, 'workers-01.csv'))
orders_df = pd.read_csv(os.path.join(script_dir, 'orders-01.csv'))

# Combine the metrics into a single DataFrame for easy processing
combined_df = service_times_df.merge(estimated_profits_df, on=['order_id', 'worker_id']).merge(delivery_costs_df,
                                                                                               on=['order_id',
                                                                                                   'worker_id'])

# Greedy Assignment Algorithm
def greedy_assignment(combined_df, workers_df, orders_df):
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

    return assignments_df

# Run the greedy assignment process
assignments_df = greedy_assignment(combined_df, workers_df, orders_df)

# Save the results to a CSV file in the same directory as the script
output_file = os.path.join(script_dir, 'greedy_assignments.csv')
assignments_df.to_csv(output_file, index=False)

# Output a few rows for quick review
print(assignments_df.head())
