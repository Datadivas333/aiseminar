import os
import pandas as pd
import random
import copy

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_dir}")

# Define paths relative to the script's location
costs_path = os.path.join(script_dir, 'delivery-costs-01.csv')
estimated_profits_path = os.path.join(script_dir, 'estimated-profits-01.csv')
initial_solutions_path = os.path.join(script_dir, 'feasible_solutions-01.csv')
orders_path = os.path.join(script_dir, 'orders-01.csv')
service_times_path = os.path.join(script_dir, 'service-times-01.csv')
workers_path = os.path.join(script_dir, 'workers-01.csv')

# Load the CSV files using relative paths
print("Loading CSV files...")
costs_df = pd.read_csv(costs_path)
estimated_profits_df = pd.read_csv(estimated_profits_path)
initial_solutions_df = pd.read_csv(initial_solutions_path)
orders_df = pd.read_csv(orders_path)
service_times_df = pd.read_csv(service_times_path)
workers_df = pd.read_csv(workers_path)
print("CSV files loaded successfully.")

# Create the list of worker IDs and order IDs
J = orders_df['order_id'].tolist()  # Order IDs
K = workers_df['worker_id'].tolist()  # Worker IDs

# Convert DataFrames to Dictionaries
print("Converting DataFrames to dictionaries...")
costs = {(row['order_id'], row['worker_id']): row['delivery_cost'] for _, row in costs_df.iterrows()}
estimated_profits = {(row['order_id'], row['worker_id']): row['estimated_profit'] for _, row in
                     estimated_profits_df.iterrows()}
service_times = {(row['order_id'], row['worker_id']): row['service_time'] for _, row in service_times_df.iterrows()}
print("Conversion to dictionaries completed.")

# Clean the initial solutions DataFrame
initial_solutions_df_cleaned = initial_solutions_df.dropna()

# Number of orders
num_orders = len(orders_df)


# Function to initialize population ensuring one-to-one assignment
def initialize_population(J, K, initial_solutions_df_cleaned, num_orders):
    initial_solutions = []
    for i in range(0, len(initial_solutions_df_cleaned), num_orders):
        solution = {}
        chunk = initial_solutions_df_cleaned.iloc[i:i + num_orders]
        for _, row in chunk.iterrows():
            order_id = int(row['order_id'])
            for worker_id in K:
                if int(row[str(worker_id)]) == 1:
                    solution[order_id] = worker_id
                    break  # Ensure only one worker per order
        initial_solutions.append(solution)
    return initial_solutions


# Define the fitness function
def fitness_function(X, service_times, costs, estimated_profits, s_max, q_k):
    total_profit = 0
    total_service_time = 0
    order_count = {k: 0 for k in q_k}

    for j, worker in X.items():
        order_count[worker] += 1
        if order_count[worker] > q_k[worker]:
            return -1

        s_jk = service_times[(j, worker)]
        p_jk = estimated_profits[(j, worker)]
        total_profit += p_jk
        total_service_time += s_jk

        if s_jk > s_max:
            return -1

    s_k = total_service_time / (len(X) * s_max)
    p_k = total_profit / len(X)

    if s_k > 1 or p_k < 0:
        return -1

    return p_k - s_k


# Updated λX calculation to ensure it's at least 1
def calculate_lambda_X(X, P, lambda_max):
    sum_f_X_prime = sum(fitness_function(X_prime, service_times, costs, estimated_profits, s_max, q_k) for X_prime in P)
    f_X = fitness_function(X, service_times, costs, estimated_profits, s_max, q_k)
    if sum_f_X_prime == 0:
        return lambda_max  # Avoid division by zero
    lambda_X = lambda_max * (sum_f_X_prime - f_X) / sum_f_X_prime
    return max(1, lambda_X)  # Ensure λX is at least 1


# Ensure one-to-one assignment during propagation
def propagate_solution(X, J, K):
    X_prime = copy.deepcopy(X)
    j = random.choice(J)
    current_worker = X_prime[j]
    available_workers = [k for k in K if k != current_worker]

    if available_workers:
        new_worker = random.choice(available_workers)
        X_prime[j] = new_worker

    return X_prime


# Define the Water Wave Optimization algorithm
def water_wave_optimization(J, K, s_max, q_k, service_times, costs, estimated_profits, P, lambda_max, max_iter=100):
    print("Starting the Water Wave Optimization...")
    X_star = max(P, key=lambda X: fitness_function(X, service_times, costs, estimated_profits, s_max, q_k))
    iter = 0
    while iter <= max_iter:
        for X in P:
            lambda_X = calculate_lambda_X(X, P, lambda_max)
            W = random.randint(1, int(lambda_X))

            X_prime = copy.deepcopy(X)
            for _ in range(W):
                X_prime = propagate_solution(X_prime, J, K)

            if fitness_function(X_prime, service_times, costs, estimated_profits, s_max, q_k) > fitness_function(X,
                                                                                                                 service_times,
                                                                                                                 costs,
                                                                                                                 estimated_profits,
                                                                                                                 s_max,
                                                                                                                 q_k):
                P.remove(X)
                P.append(X_prime)

                if fitness_function(X_prime, service_times, costs, estimated_profits, s_max, q_k) > fitness_function(
                        X_star, service_times, costs, estimated_profits, s_max, q_k):
                    X_star = X_prime

            nb = random.randint(1, len(K))
            for _ in range(nb):
                X_n = copy.deepcopy(X_star)
                X_n = propagate_solution(X_n, J, K)

                if fitness_function(X_n, service_times, costs, estimated_profits, s_max, q_k) > fitness_function(X_star,
                                                                                                                 service_times,
                                                                                                                 costs,
                                                                                                                 estimated_profits,
                                                                                                                 s_max,
                                                                                                                 q_k):
                    X_star = X_n

        iter += 1
    print("Finished the optimization.")
    return X_star


# Initialize population with the corrected method
initial_solutions = initialize_population(J, K, initial_solutions_df_cleaned, num_orders)

# Example usage
s_max = 15  # Example value, adjust as necessary
q_k = {worker_id: 1 for worker_id in K}  # Worker capacity set to 1 for all workers
lambda_max = len(J)  # Maximum allowable wavelength

# Run the Water Wave Optimization algorithm using the loaded data
X_star = water_wave_optimization(J, K, s_max, q_k, service_times, costs, estimated_profits, initial_solutions,
                                 lambda_max)

# Convert the result to a DataFrame with additional metrics
output_rows = []
for j, k in X_star.items():
    service_time = service_times[(j, k)]
    delivery_cost = costs[(j, k)]
    estimated_profit = estimated_profits[(j, k)]

    output_rows.append({
        "order_id": j,
        "worker_id": k,
        "service_time": service_time,
        "delivery_cost": delivery_cost,
        "estimated_profit": estimated_profit
    })

print("Creating output DataFrame...")
output_df = pd.DataFrame(output_rows)

# Save the result to a CSV file
output_file = os.path.join(script_dir, 'optimal_assignment_with_metrics.csv')
print(f"Saving output to {output_file}...")
output_df.to_csv(output_file, index=False)

print("Output saved successfully.")
