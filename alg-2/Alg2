import pandas as pd  # Importing the pandas library for data manipulation and analysis
import os  # Importing the os library for interacting with the operating system (e.g., file paths)

def calculate_utility(p_ow, s_ow):
    """
    Calculate the utility of assigning an order to a worker.
    
    Parameters:
    p_ow (float): Estimated profit for assigning order o to worker w.
    s_ow (float): Service time for assigning order o to worker w.
    
    Returns:
    float: The utility, which is the difference between the estimated profit and the service time.
    """
    return p_ow - s_ow

def is_valid_assignment(X, o, w, service_times, s_max):
    """
    Check if assigning a specific order to a specific worker is valid.
    
    Parameters:
    X (dict): The current assignment matrix tracking which orders have been assigned to which workers.
    o (int): The ID of the order to be assigned.
    w (int): The ID of the worker to whom the order may be assigned.
    service_times (DataFrame): A DataFrame containing the service times for each (order, worker) pair.
    s_max (float): The maximum allowable service time for any order-worker assignment.
    
    Returns:
    bool: True if the assignment is valid, False otherwise.
    """
    # Check if the worker is already assigned to another order
    if any(X[o2][w] == 1 for o2 in X):
        print(f"Worker {w} is already assigned to another order.")
        return False

    # Check if the service time exceeds the maximum allowable service time
    service_time = service_times.at[(o, w), 'service_time']
    if service_time > s_max:
        print(f"Service time for order {o} with worker {w} is {service_time}, exceeding s_max {s_max}.")
        return False

    return True

def backtrack(X, orders, workers, service_times, estimated_profits, s_max, solutions, order_index=0, max_solutions=10):
    """
    Use backtracking to generate all feasible solutions for assigning orders to workers.
    
    Parameters:
    X (dict): The current assignment matrix.
    orders (list): A list of all order IDs.
    workers (list): A list of all worker IDs.
    service_times (DataFrame): A DataFrame containing the service times for each (order, worker) pair.
    estimated_profits (DataFrame): A DataFrame containing the estimated profits for each (order, worker) pair.
    s_max (float): The maximum allowable service time for any assignment.
    solutions (list): A list to store all feasible solutions found.
    order_index (int): The current index of the order being processed.
    max_solutions (int): The maximum number of solutions to find before stopping.
    
    Returns:
    None
    """
    if len(solutions) >= max_solutions:
        return  # Stop if the maximum number of solutions is reached

    if order_index == len(orders):
        # All orders have been assigned, so store this solution
        solution = [[X[o][w] for w in workers] for o in orders]
        solutions.append(solution)
        print(f"Solution found: {solution}")
        return

    o = orders[order_index]

    for w in workers:
        if is_valid_assignment(X, o, w, service_times, s_max):
            # Assign the order to the worker
            X[o][w] = 1
            print(f"Assigning order {o} to worker {w} at order index {order_index}")
            
            # Recursively try to assign the next order
            backtrack(X, orders, workers, service_times, estimated_profits, s_max, solutions, order_index + 1, max_solutions)
            
            # Unassign the order (backtracking)
            X[o][w] = 0
            print(f"Unassigning order {o} from worker {w} at order index {order_index}")

def generate_all_feasible_solutions(orders, workers, service_times, estimated_profits, s_max, max_solutions=10):
    """
    Generate all feasible solutions for the order assignment problem using backtracking.
    
    Parameters:
    orders (list): A list of all order IDs.
    workers (list): A list of all worker IDs.
    service_times (DataFrame): A DataFrame containing the service times for each (order, worker) pair.
    estimated_profits (DataFrame): A DataFrame containing the estimated profits for each (order, worker) pair.
    s_max (float): The maximum allowable service time for any assignment.
    max_solutions (int): The maximum number of solutions to generate.
    
    Returns:
    list: A list of all feasible solutions found.
    """
    # Initialize the assignment matrix with all zeros
    X = {o: {w: 0 for w in workers} for o in orders}
    solutions = []
    
    # Start the backtracking process to find all solutions
    backtrack(X, orders, workers, service_times, estimated_profits, s_max, solutions, max_solutions=max_solutions)
    
    return solutions

def algorithm_2(orders_file, workers_file, service_times_file, estimated_profits_file, s_max, output_file, max_solutions=10):
    """
    Main function to execute the order assignment algorithm.
    
    Parameters:
    orders_file (str): Path to the CSV file containing order data.
    workers_file (str): Path to the CSV file containing worker data.
    service_times_file (str): Path to the CSV file containing service time data.
    estimated_profits_file (str): Path to the CSV file containing estimated profit data.
    s_max (float): The maximum allowable service time for any assignment.
    output_file (str): Path to the output CSV file where the solutions will be saved.
    max_solutions (int): The maximum number of solutions to generate and save.
    
    Returns:
    None
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
s_max = 63

# Define the maximum number of solutions to find
max_solutions = 30  # Adjust this as needed

# Define file paths
base_dir = os.path.dirname(__file__)

orders_file = os.path.join(base_dir, 'orders-01.csv')
workers_file = os.path.join(base_dir, 'workers-01.csv')
service_times_file = os.path.join(base_dir, 'service-times-01.csv')
estimated_profits_file = os.path.join(base_dir, 'estimated-profits-01.csv')
output_file = os.path.join(base_dir, 'all_feasible_solutions.csv')

# Run the algorithm to generate a limited number of feasible solutions
algorithm_2(orders_file, workers_file, service_times_file, estimated_profits_file, s_max, output_file, max_solutions)
