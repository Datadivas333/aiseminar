import pandas as pd
import os


def calculate_utility(p_ow, s_ow):
    """
    Calculate the utility of assigning an order to a worker.
    Utility is the estimated profit minus the service time.
    """
    return p_ow - s_ow


def is_valid_assignment(X, o, w, service_times, s_max):
    """
    Check if assigning a specific order to a specific worker is valid.
    """
    # Check if the worker is already assigned to another order
    if any(X[o2][w] == 1 for o2 in X):
        return False

    # Check if the service time exceeds the maximum allowable service time
    service_time = service_times.at[(o, w), 'service_time']
    if service_time > s_max:
        return False

    return True


def backtrack_with_early_stop(X, orders, workers, service_times, estimated_profits, s_max, solutions, order_index=0, max_solutions=10):
    """
    Enhanced backtracking function with early stopping based on max_solutions.
    """
    if len(solutions) >= max_solutions:
        return  # Stop if the maximum number of solutions is reached

    if order_index == len(orders):
        # All orders have been assigned, so store this solution
        solution = [[X[o][w] for w in workers] for o in orders]
        solutions.append(solution)
        return

    o = orders[order_index]

    for w in workers:
        if is_valid_assignment(X, o, w, service_times, s_max):
            # Assign the order to the worker
            X[o][w] = 1
            print(f"Assigning order {o} to worker {w} at order index {order_index}")  # Progress log

            # Recursively try to assign the next order
            backtrack_with_early_stop(X, orders, workers, service_times, estimated_profits, s_max, solutions, order_index + 1, max_solutions)

            # Unassign the order (backtracking)
            X[o][w] = 0
            print(f"Unassigning order {o} from worker {w} at order index {order_index}")  # Progress log


def generate_all_feasible_solutions(orders, workers, service_times, estimated_profits, s_max, max_solutions=10):
    """
    Generate all feasible solutions for the order assignment problem using backtracking.
    """
    X = {o: {w: 0 for w in workers} for o in orders}
    solutions = []
    backtrack_with_early_stop(X, orders, workers, service_times, estimated_profits, s_max, solutions, max_solutions=max_solutions)
    return solutions


def algorithm_2(orders_file, workers_file, service_times_file, estimated_profits_file, s_max, output_file, max_solutions=10):
    """
    Main function to execute the order assignment algorithm.
    """
    try:
        print("Reading input files...")
        # Load the order, worker, service time, and estimated profit data from CSV files
        orders_df = pd.read_csv(orders_file)
        workers_df = pd.read_csv(workers_file)
        service_times = pd.read_csv(service_times_file, index_col=[0, 1])
        estimated_profits = pd.read_csv(estimated_profits_file, index_col=[0, 1])

        # Extract lists of order IDs and worker IDs
        orders = orders_df['order_id'].tolist()
        workers = workers_df['worker_id'].tolist()

        print(f"Number of orders: {len(orders)}")
        print(f"Number of workers: {len(workers)}")

        # Generate all feasible solutions
        all_solutions = generate_all_feasible_solutions(orders, workers, service_times, estimated_profits, s_max, max_solutions)

        if not all_solutions:
            print("No feasible solutions found.")
            return

        # Prepare a DataFrame to store the solutions
        columns = ['order_id'] + workers
        final_df = pd.DataFrame(columns=columns)

        # Convert each solution to a DataFrame and append it to the final DataFrame
        for solution in all_solutions:
            temp_df = pd.DataFrame(solution, columns=workers)
            temp_df.insert(0, 'order_id', orders)
            final_df = pd.concat([final_df, temp_df], axis=0)

        # Save the solutions to the output CSV file
        final_df.to_csv(output_file, index=False)
        print(f"All feasible solutions saved to {output_file}.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Set the maximum service time constraint
s_max = 100

# Define the maximum number of solutions to find
max_solutions = 1  # Only produce 1 solution

# Define file paths
base_dir = os.path.dirname(__file__)

orders_file = os.path.join(base_dir, 'orders-01.csv')
workers_file = os.path.join(base_dir, 'workers-01.csv')
service_times_file = os.path.join(base_dir, 'service-times-01.csv')
estimated_profits_file = os.path.join(base_dir, 'estimated-profits-01.csv')
output_file = os.path.join(base_dir, 'all_feasible_solutions.csv')

# Run the algorithm to generate a limited number of feasible solutions
algorithm_2(orders_file, workers_file, service_times_file, estimated_profits_file, s_max, output_file, max_solutions)
