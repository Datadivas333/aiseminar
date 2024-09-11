import pandas as pd
import os


def calculate_utility(p_ow, s_ow):
    return p_ow - s_ow


def is_valid_assignment(X, o, w, service_times, s_max):
    if any(X[o2][w] == 1 for o2 in X):
        return False
    service_time = service_times.at[(o, w), 'service_time']
    if service_time > s_max:
        return False
    return True


def backtrack_with_early_stop(X, orders, workers, service_times, estimated_profits, s_max, solutions, order_index=0, max_solutions=10):
    if len(solutions) >= max_solutions:
        return
    if order_index == len(orders):
        solution = [[X[o][w] for w in workers] for o in orders]
        solutions.append(solution)
        return
    o = orders[order_index]
    for w in workers:
        if is_valid_assignment(X, o, w, service_times, s_max):
            X[o][w] = 1
            backtrack_with_early_stop(X, orders, workers, service_times, estimated_profits, s_max, solutions, order_index + 1, max_solutions)
            X[o][w] = 0


def generate_all_feasible_solutions(orders, workers, service_times, estimated_profits, s_max, max_solutions=10):
    X = {o: {w: 0 for w in workers} for o in orders}
    solutions = []
    backtrack_with_early_stop(X, orders, workers, service_times, estimated_profits, s_max, solutions, max_solutions=max_solutions)
    return solutions


def algorithm_2(orders_file, workers_file, service_times_file, estimated_profits_file, s_max, output_file, max_solutions=10):
    try:
        orders_df = pd.read_csv(orders_file)
        workers_df = pd.read_csv(workers_file)
        service_times = pd.read_csv(service_times_file, index_col=[0, 1])
        estimated_profits = pd.read_csv(estimated_profits_file, index_col=[0, 1])

        orders = orders_df['order_id'].tolist()
        workers = workers_df['worker_id'].tolist()

        all_solutions = generate_all_feasible_solutions(orders, workers, service_times, estimated_profits, s_max, max_solutions)

        if not all_solutions:
            print("No feasible solutions found.")
            return

        columns = ['order_id'] + workers
        final_df = pd.DataFrame(columns=columns)

        for solution in all_solutions:
            temp_df = pd.DataFrame(solution, columns=workers)
            temp_df.insert(0, 'order_id', orders)
            final_df = pd.concat([final_df, temp_df], axis=0)

        final_df.to_csv(output_file, index=False)
        print(f"Solutions saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


def process_all_instances(base_input_dir, base_output_dir, s_max, max_solutions):
    instances = ['instance-01', 'instance-02', 'instance-03']

    for instance in instances:
        input_folder = os.path.join(base_input_dir, instance)
        output_folder = os.path.join(base_output_dir, instance)

        # Ensure the output folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Extract the instance number (e.g., '01', '02', '03')
        instance_number = instance.split('-')[-1]

        # Input files for this instance
        orders_file = os.path.join(input_folder, f'orders-{instance_number}.csv')
        workers_file = os.path.join(input_folder, f'workers-{instance_number}.csv')
        service_times_file = os.path.join(input_folder, f'service-times-{instance_number}.csv')
        estimated_profits_file = os.path.join(input_folder, f'estimated-profits-{instance_number}.csv')

        # Output file for this instance
        output_file = os.path.join(output_folder, f'feasible_solutions-{instance_number}.csv')

        # Process the instance
        print(f"Processing {instance}...")
        algorithm_2(orders_file, workers_file, service_times_file, estimated_profits_file, s_max, output_file, max_solutions)


# Set base directory paths
base_input_dir = os.path.join(os.path.dirname(__file__), 'alg2-inputs')
base_output_dir = os.path.join(os.path.dirname(__file__), 'alg2-outputs')

# Set the maximum service time and number of solutions
s_max = 100
max_solutions = 20

# Process all instances
process_all_instances(base_input_dir, base_output_dir, s_max, max_solutions)

