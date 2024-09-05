import os
import pandas as pd

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_dir}")

# Define paths to the data files directly in the SUMMARY folder
greedy_01_path = os.path.join(script_dir, 'greedy_assignments-01.csv')
greedy_02_path = os.path.join(script_dir, 'greedy_assignments-02.csv')
greedy_03_path = os.path.join(script_dir, 'greedy_assignments-03.csv')

optimal_01_path = os.path.join(script_dir, 'optimal_assignment_01.csv')
optimal_02_path = os.path.join(script_dir, 'optimal_assignment_02.csv')
optimal_03_path = os.path.join(script_dir, 'optimal_assignment_03.csv')

# Print file paths for debugging
print(f"Greedy Assignment 01 Path: {greedy_01_path}")
print(f"Greedy Assignment 02 Path: {greedy_02_path}")
print(f"Greedy Assignment 03 Path: {greedy_03_path}")

print(f"Optimal Assignment 01 Path: {optimal_01_path}")
print(f"Optimal Assignment 02 Path: {optimal_02_path}")
print(f"Optimal Assignment 03 Path: {optimal_03_path}")

# Try to load the files and print debugging information
try:
    # Load the greedy assignment files
    greedy_assignments_01 = pd.read_csv(greedy_01_path)
    greedy_assignments_02 = pd.read_csv(greedy_02_path)
    greedy_assignments_03 = pd.read_csv(greedy_03_path)

    # Load the optimal assignment files
    optimal_assignment_01 = pd.read_csv(optimal_01_path)
    optimal_assignment_02 = pd.read_csv(optimal_02_path)
    optimal_assignment_03 = pd.read_csv(optimal_03_path)

    # Combine all greedy assignments and optimal assignments
    greedy_assignments = pd.concat([greedy_assignments_01, greedy_assignments_02, greedy_assignments_03])
    optimal_assignments = pd.concat([optimal_assignment_01, optimal_assignment_02, optimal_assignment_03])

    # Calculate the average service time and delivery cost for both methods
    greedy_avg_service_time = greedy_assignments['service_time'].mean()
    greedy_avg_cost = greedy_assignments['delivery_cost'].mean()

    optimal_avg_service_time = optimal_assignments['service_time'].mean()
    optimal_avg_cost = optimal_assignments['delivery_cost'].mean()

    # Display the results
    print("Comparison of Average Service Time and Cost:")
    print(f"Greedy Method - Average Service Time: {greedy_avg_service_time}, Average Delivery Cost: {greedy_avg_cost}")
    print(f"Optimal Method - Average Service Time: {optimal_avg_service_time}, Average Delivery Cost: {optimal_avg_cost}")

except FileNotFoundError as e:
    print(f"Error: {e}. Please make sure the file exists at the specified path.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
