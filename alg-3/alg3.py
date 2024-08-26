import os
import pandas as pd
import random

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_dir}")

# Define paths relative to the script's location
costs_path = os.path.join(script_dir, 'costs.csv')
estimated_profits_path = os.path.join(script_dir, 'estimated_profits.csv')
initial_solutions_path = os.path.join(script_dir, 'initial_solutions.csv')
orders_path = os.path.join(script_dir, 'orders.csv')
service_times_path = os.path.join(script_dir, 'service_times.csv')
workers_path = os.path.join(script_dir, 'workers.csv')

# Print out the paths to ensure they are correct
print(f"Looking for costs.csv at: {costs_path}")

# Load the CSV files using relative paths
print("Loading CSV files...")
costs_df = pd.read_csv(costs_path)
estimated_profits_df = pd.read_csv(estimated_profits_path)
initial_solutions_df = pd.read_csv(initial_solutions_path)
orders_df = pd.read_csv(orders_path)
service_times_df = pd.read_csv(service_times_path)
workers_df = pd.read_csv(workers_path)
print("CSV files loaded successfully.")

# Create the list of worker IDs
K = workers_df['worker_id'].tolist()  # List of worker IDs

# Convert DataFrames to Dictionaries
print("Converting DataFrames to dictionaries...")
costs = {(row['order_id'], row['worker_id']): row['cost'] for _, row in costs_df.iterrows()}
estimated_profits = {(row['order_id'], row['worker_id']): row['estimated_profit'] for _, row in estimated_profits_df.iterrows()}
service_times = {(row['order_id'], row['worker_id']): row['service_time'] for _, row in service_times_df.iterrows()}
print("Conversion to dictionaries completed.")

# Clean the initial solutions DataFrame
initial_solutions_df_cleaned = initial_solutions_df.dropna()

# Convert the cleaned initial solutions DataFrame into a list of dictionaries
initial_solutions = []
num_orders = len(orders_df)  # Number of orders

print("Processing initial solutions...")
# Process each chunk of rows as a separate matrix
for i in range(0, len(initial_solutions_df_cleaned), num_orders):
    solution = {}
    chunk = initial_solutions_df_cleaned.iloc[i:i+num_orders]
    for _, row in chunk.iterrows():
        order_id = int(row['order_id'])
        solution[order_id] = {worker_id: int(row[str(worker_id)]) for worker_id in K}
    initial_solutions.append(solution)
print("Initial solutions processed.")

# Define the fitness function
def fitness_function(X, service_times, costs, estimated_profits, s_max, q_k):
    total_profit = 0
    total_service_time = 0
    order_count = {k: 0 for k in q_k}

    for j, workers in X.items():
        for k, assigned in workers.items():
            if assigned == 1:
                order_count[k] += 1
                if order_count[k] > q_k[k]:
                    return -1

                s_jk = service_times[(j, k)]
                p_jk = estimated_profits[(j, k)]
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

# Define the Water Wave Optimization algorithm
def water_wave_optimization(J, K, s_max, q_k, service_times, costs, estimated_profits, P, lambda_max, max_iter=100):
    print("Starting the Water Wave Optimization...")
    X_star = max(P, key=lambda X: fitness_function(X, service_times, costs, estimated_profits, s_max, q_k))
    iter = 0
    while iter <= max_iter:
        for X in P:
            lambda_X = calculate_lambda_X(X, P, lambda_max)
            W = random.randint(1, int(lambda_X))

            X_prime = X.copy()
            for _ in range(W):
                j = random.choice(J)
                k = random.choice(K)
                X_prime[j][k] = 1 - X_prime[j][k]

            if fitness_function(X_prime, service_times, costs, estimated_profits, s_max, q_k) > fitness_function(X, service_times, costs, estimated_profits, s_max, q_k):
                P.remove(X)
                P.append(X_prime)

                if fitness_function(X_prime, service_times, costs, estimated_profits, s_max, q_k) > fitness_function(X_star, service_times, costs, estimated_profits, s_max, q_k):
                    X_star = X_prime

            nb = random.randint(1, len(K))
            for _ in range(nb):
                X_n = X_star.copy()
                j = random.choice(J)
                k = random.choice(K)
                X_n[j][k] = 1 - X_n[j][k]

                if fitness_function(X_n, service_times, costs, estimated_profits, s_max, q_k) > fitness_function(X_star, service_times, costs, estimated_profits, s_max, q_k):
                    X_star = X_n

        iter += 1
    print("Finished the optimization.")
    return X_star

# Example usage
J = orders_df['order_id'].tolist()  # Order IDs
K = workers_df['worker_id'].tolist()  # Worker IDs
s_max = 15  # Example value, adjust as necessary
q_k = {worker_id: 1 for worker_id in K}  # Worker capacity set to 1 for all workers
lambda_max = len(J)  # Maximum allowable wavelength

# Run the Water Wave Optimization algorithm using the loaded data
X_star = water_wave_optimization(J, K, s_max, q_k, service_times, costs, estimated_profits, initial_solutions, lambda_max)

# Convert the result to a DataFrame
output_rows = []
for j in J:  # J is the list of orders
    for k in K:  # K is the list of workers
        if X_star[j][k] == 1:
            output_rows.append({"order_id": j, "worker_id": k})
            break  # Break after assigning to one worker

# If your solution allows for errors and you get multiple assignments for one order, you need to catch that.
# Here's a sanity check to ensure only one worker is assigned per order
final_output = []
assigned_orders = set()

for row in output_rows:
    if row["order_id"] not in assigned_orders:
        final_output.append(row)
        assigned_orders.add(row["order_id"])

output_df = pd.DataFrame(final_output)
output_file = os.path.join(script_dir, 'optimal_assignment.csv')
output_df.to_csv(output_file, index=False)
print(f"Optimal assignment saved to {output_file}.")