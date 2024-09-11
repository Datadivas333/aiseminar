import os
import pandas as pd
import random

# Define base directories for inputs and outputs
input_base_dir = '/aiseminar/Naive/input'
output_base_dir = '/aiseminar/Naive/output'
instance_numbers = ['01', '02', '03']  # Define the instances

# Function to implement a random assignment method
def random_assignment(instance_number, orders_file, workers_file, service_times_file, delivery_costs_file, estimated_profits_file):
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

        # Randomly assign workers to orders
        random_assignments = []
        for order in orders:
            assigned_worker = random.choice(workers)  # Randomly assign a worker
            # Get corresponding service time, delivery cost, and estimated profit from data
            service_time = random.uniform(30, 60)  # Example random service time
            delivery_cost = random.uniform(3, 7)  # Example random delivery cost
            random_assignments.append({
                'order_id': order,
                'worker_id': assigned_worker,
                'service_time': service_time,
                'delivery_cost': delivery_cost
            })

        # Convert to DataFrame with the same structure as your greedy assignments
        random_assignments_df = pd.DataFrame(random_assignments)

        # Calculate and print summary statistics
        avg_service_time = random_assignments_df['service_time'].mean()
        avg_delivery_cost = random_assignments_df['delivery_cost'].mean()
        print(f"\nRandom Assignment Results for Instance {instance_number}:")
        print(f"Average Service Time: {avg_service_time}")
        print(f"Average Delivery Cost: {avg_delivery_cost}")

        # Save the random assignments to a CSV file with the same structure as greedy assignments
        output_file = os.path.join(output_base_dir, f'random_assignments_{instance_number}.csv')
        random_assignments_df.to_csv(output_file, index=False)
        print(f"Random assignments saved to {output_file}")
    
    except FileNotFoundError as e:
        print(f"Error: {e}. Please make sure the file exists at the specified path for instance {instance_number}.")
    except Exception as e:
        print(f"An unexpected error occurred in instance {instance_number}: {e}")

# Loop over each instance and run the random assignment method
for instance_number in instance_numbers:
    print(f"Processing Instance {instance_number} with Random Assignment...")

    # Define file paths for the current instance
    instance_input_dir = os.path.join(input_base_dir, f'instance-{instance_number}')
    orders_file = os.path.join(instance_input_dir, f'orders-{instance_number}.csv')
    workers_file = os.path.join(instance_input_dir, f'workers-{instance_number}.csv')
    service_times_file = os.path.join(instance_input_dir, f'service-times-{instance_number}.csv')
    delivery_costs_file = os.path.join(instance_input_dir, f'delivery-costs-{instance_number}.csv')
    estimated_profits_file = os.path.join(instance_input_dir, f'estimated-profits-{instance_number}.csv')

    # Run the random assignment method for this instance
    random_assignment(instance_number, orders_file, workers_file, service_times_file, delivery_costs_file, estimated_profits_file)
