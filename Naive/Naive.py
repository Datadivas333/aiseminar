import os
import pandas as pd
import random

# Define base directories for inputs and outputs
input_base_dir = 'Naive/input'
output_base_dir = 'Naive/output'
instance_numbers = ['01', '02', '03']  # Define the instances

# Set a random seed for reproducibility
random_seed = 42  # You can choose any seed value

# Function to implement a one-to-one random assignment method
def random_assignment_one_to_one(instance_number, orders_file, workers_file, service_times_file, delivery_costs_file, estimated_profits_file):
    try:
        # Load the orders, workers, service times, delivery costs, and estimated profits data
        orders_df = pd.read_csv(orders_file)
        workers_df = pd.read_csv(workers_file)
        service_times_df = pd.read_csv(service_times_file)
        delivery_costs_df = pd.read_csv(delivery_costs_file)
        estimated_profits_df = pd.read_csv(estimated_profits_file)
        
        # Extract order and worker IDs
        orders = orders_df['order_id'].tolist()
        workers = workers_df['worker_id'].tolist()

        # Check if the number of orders and workers are equal for a one-to-one assignment
        if len(orders) != len(workers):
            print(f"Error: The number of orders ({len(orders)}) and workers ({len(workers)}) must be equal for a one-to-one assignment.")
            return

        # Set the random seed before shuffling the workers to ensure reproducibility
        random.seed(random_seed)
        random.shuffle(workers)

        # Assign each worker to exactly one order (one-to-one mapping)
        random_assignments = []
        for order, worker in zip(orders, workers):
            # Retrieve corresponding service time, delivery cost, and estimated profit
            service_time = service_times_df.loc[(service_times_df['order_id'] == order) & (service_times_df['worker_id'] == worker), 'service_time'].values[0]
            delivery_cost = delivery_costs_df.loc[(delivery_costs_df['order_id'] == order) & (delivery_costs_df['worker_id'] == worker), 'delivery_cost'].values[0]
            estimated_profit = estimated_profits_df.loc[(estimated_profits_df['order_id'] == order) & (estimated_profits_df['worker_id'] == worker), 'estimated_profit'].values[0]
            
            random_assignments.append({
                'order_id': order,
                'worker_id': worker,
                'service_time': service_time,
                'delivery_cost': delivery_cost,
                'estimated_profit': estimated_profit
            })

        # Convert to DataFrame with the same structure as your other assignments
        random_assignments_df = pd.DataFrame(random_assignments)

        # Calculate and print summary statistics
        avg_service_time = random_assignments_df['service_time'].mean()
        avg_delivery_cost = random_assignments_df['delivery_cost'].mean()
        avg_estimated_profit = random_assignments_df['estimated_profit'].mean()
        print(f"\nRandom Assignment Results for Instance {instance_number}:")
        print(f"Average Service Time: {avg_service_time}")
        print(f"Average Delivery Cost: {avg_delivery_cost}")
        print(f"Average Estimated Profit: {avg_estimated_profit}")

        # Save the random assignments to a CSV file with the same structure as greedy assignments
        output_file = os.path.join(output_base_dir, f'random_assignments_{instance_number}.csv')
        random_assignments_df.to_csv(output_file, index=False)
        print(f"Random assignments saved to {output_file}")
    
    except FileNotFoundError as e:
        print(f"Error: {e}. Please make sure the file exists at the specified path for instance {instance_number}.")
    except Exception as e:
        print(f"An unexpected error occurred in instance {instance_number}: {e}")

# Loop over each instance and run the random one-to-one assignment method
for instance_number in instance_numbers:
    print(f"Processing Instance {instance_number} with Random One-to-One Assignment...")

    # Define file paths for the current instance
    instance_input_dir = os.path.join(input_base_dir, f'instance-{instance_number}')
    orders_file = os.path.join(instance_input_dir, f'orders-{instance_number}.csv')
    workers_file = os.path.join(instance_input_dir, f'workers-{instance_number}.csv')
    service_times_file = os.path.join(instance_input_dir, f'service-times-{instance_number}.csv')
    delivery_costs_file = os.path.join(instance_input_dir, f'delivery-costs-{instance_number}.csv')
    estimated_profits_file = os.path.join(instance_input_dir, f'estimated-profits-{instance_number}.csv')

    # Run the random assignment method for this instance
    random_assignment_one_to_one(instance_number, orders_file, workers_file, service_times_file, delivery_costs_file, estimated_profits_file)
