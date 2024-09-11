import os
import pandas as pd
import random
import copy

# Define base directories for inputs and outputs
input_base_dir = 'alg-3/alg3-inputs'
output_base_dir = 'alg-3/alg3-outputs'

# Define instance numbers
instance_numbers = ['01', '02', '03']

# Loop over all instances
for instance_num in instance_numbers:
    print(f"Processing instance {instance_num}...")

    # Define paths relative to the base input directory
    instance_input_dir = os.path.join(input_base_dir, f'instance-{instance_num}')
    costs_path = os.path.join(instance_input_dir, f'delivery-costs-{instance_num}.csv')
    estimated_profits_path = os.path.join(instance_input_dir, f'estimated-profits-{instance_num}.csv')
    initial_solutions_path = os.path.join(instance_input_dir, f'all_feasible_solutions_{instance_num}.csv')
    orders_path = os.path.join(instance_input_dir, f'orders-{instance_num}.csv')
    service_times_path = os.path.join(instance_input_dir, f'service-times-{instance_num}.csv')
    workers_path = os.path.join(instance_input_dir, f'workers-{instance_num}.csv')

    # Load the CSV files for this instance
    print("Loading CSV files...")
    costs_df = pd.read_csv(costs_path)
    estimated_profits_df = pd.read_csv(estimated_profits_path)
    initial_solutions_df = pd.read_csv(initial_solutions_path)
    orders_df = pd.read_csv(orders_path)
    service_times_df = pd.read_csv(service_times_path)
    workers_df = pd.read_csv(workers_path)
    print("CSV files loaded successfully.")

    # Create the list of worker IDs and order IDs
    O = orders_df['order_id'].tolist()  # Order IDs
    W = workers_df['worker_id'].tolist()  # Worker IDs

    # Convert DataFrames to Dictionaries
    print("Converting DataFrames to dictionaries...")
    costs = {(row['order_id'], row['worker_id']): row['delivery_cost'] for _, row in costs_df.iterrows()}
    estimated_profits = {(row['order_id'], row['worker_id']): row['estimated_profit'] for _, row in estimated_profits_df.iterrows()}
    service_times = {(row['order_id'], row['worker_id']): row['service_time'] for _, row in service_times_df.iterrows()}
    print("Conversion to dictionaries completed.")

    # Clean the initial solutions DataFrame
    initial_solutions_df_cleaned = initial_solutions_df.dropna()

    # Number of orders
    num_orders = len(orders_df)

    # Function to initialize population ensuring one-to-one assignment
    def initialize_population(O, W, initial_solutions_df_cleaned, num_orders):
        initial_solutions = []
        for i in range(0, len(initial_solutions_df_cleaned), num_orders):
            solution = {}
            chunk = initial_solutions_df_cleaned.iloc[i:i + num_orders]
            for _, row in chunk.iterrows():
                order_id = int(row['order_id'])
                for worker_id in W:
                    if int(row[str(worker_id)]) == 1:
                        solution[order_id] = worker_id
                        break  # Ensure only one worker per order
            initial_solutions.append(solution)
        return initial_solutions

    # Define the fitness function
    def fitness_function(X, service_times, costs, estimated_profits, s_max, q_w):
        total_profit = 0
        total_service_time = 0
        order_count = {worker: 0 for worker in q_w}

        for o, worker in X.items():
            order_count[worker] += 1
            if order_count[worker] > q_w[worker]:
                return -1

            s_ow = service_times[(o, worker)]
            p_ow = estimated_profits[(o, worker)]
            total_profit += p_ow
            total_service_time += s_ow

            if s_ow > s_max:
                return -1

        s_w = total_service_time / (len(X) * s_max)
        p_w = total_profit / len(X)

        if s_w > 1 or p_w < 0:
            return -1

        return p_w - s_w

    # Updated λX calculation to ensure it's at least 1
    def calculate_lambda_X(X, P, lambda_max):
        sum_f_X_prime = sum(fitness_function(X_prime, service_times, costs, estimated_profits, s_max, q_w) for X_prime in P)
        f_X = fitness_function(X, service_times, costs, estimated_profits, s_max, q_w)
        if sum_f_X_prime == 0:
            return lambda_max  # Avoid division by zero
        lambda_X = lambda_max * (sum_f_X_prime - f_X) / sum_f_X_prime
        return max(1, lambda_X)  # Ensure λX is at least 1

    # Ensure one-to-one assignment during propagation
    def propagate_solution(X, O, W):
        X_prime = copy.deepcopy(X)
        selected_order = random.choice(O)  # Changed variable name to avoid reassignment of O
        current_worker = X_prime[selected_order]
        available_workers = [worker for worker in W if worker != current_worker]

        if available_workers:
            new_worker = random.choice(available_workers)
            X_prime[selected_order] = new_worker

        return X_prime

    # Define the Water Wave Optimization algorithm
    def water_wave_optimization(O, W, s_max, q_w, service_times, costs, estimated_profits, P, lambda_max, max_iter=100):
        print("Starting the Water Wave Optimization...")
        X_star = max(P, key=lambda X: fitness_function(X, service_times, costs, estimated_profits, s_max, q_w))
        iter = 0
        while iter <= max_iter:
            for X in P:
                lambda_X = calculate_lambda_X(X, P, lambda_max)
                W_iter = random.randint(1, int(lambda_X))  # Changed variable name to avoid collision with W

                X_prime = copy.deepcopy(X)
                for _ in range(W_iter):
                    X_prime = propagate_solution(X_prime, O, W)

                if fitness_function(X_prime, service_times, costs, estimated_profits, s_max, q_w) > fitness_function(X, service_times, costs, estimated_profits, s_max, q_w):
                    P.remove(X)
                    P.append(X_prime)

                    if fitness_function(X_prime, service_times, costs, estimated_profits, s_max, q_w) > fitness_function(X_star, service_times, costs, estimated_profits, s_max, q_w):
                        X_star = X_prime

                nb = random.randint(1, len(W))
                for _ in range(nb):
                    X_n = copy.deepcopy(X_star)
                    X_n = propagate_solution(X_n, O, W)

                    if fitness_function(X_n, service_times, costs, estimated_profits, s_max, q_w) > fitness_function(X_star, service_times, costs, estimated_profits, s_max, q_w):
                        X_star = X_n

            iter += 1
        print("Finished the optimization.")
        return X_star

    # Initialize population with the corrected method
    initial_solutions = initialize_population(O, W, initial_solutions_df_cleaned, num_orders)

    # Example usage
    s_max = 15  # Example value, adjust as necessary
    q_w = {worker_id: 1 for worker_id in W}  # Worker capacity set to 1 for all workers
    lambda_max = len(O)  # Maximum allowable wavelength

    # Run the Water Wave Optimization algorithm using the loaded data
    X_star = water_wave_optimization(O, W, s_max, q_w, service_times, costs, estimated_profits, initial_solutions, lambda_max)

    # Convert the result to a DataFrame with additional metrics
    output_rows = []
    for o, w in X_star.items():
        service_time = service_times[(o, w)]
        delivery_cost = costs[(o, w)]
        estimated_profit = estimated_profits[(o, w)]

        output_rows.append({
            "order_id": o,
            "worker_id": w,
            "service_time": service_time,
            "delivery_cost": delivery_cost,
            "estimated_profit": estimated_profit
        })

    # Creating the output DataFrame
    print(f"Creating output DataFrame for instance {instance_num}...")
    output_df = pd.DataFrame(output_rows)

    # Define output path for this instance
    instance_output_dir = os.path.join(output_base_dir, f'instance-{instance_num}')
    os.makedirs(instance_output_dir, exist_ok=True)  # Ensure the directory exists
    output_file = os.path.join(instance_output_dir, 'optimal_assignment.csv')

    # Save the result to a CSV file
    print(f"Saving output to {output_file}...")
    output_df.to_csv(output_file, index=False)

    print(f"Output saved successfully for instance {instance_num}.")
