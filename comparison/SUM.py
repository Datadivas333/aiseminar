import os
import pandas as pd

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_dir}")

# Define paths to the data files for each instance
paths = {
    '01': {
        'greedy': os.path.join(script_dir, 'greedy_assignments-01.csv'),
        'optimal': os.path.join(script_dir, 'optimal_assignment_01.csv')
    },
    '02': {
        'greedy': os.path.join(script_dir, 'greedy_assignments-02.csv'),
        'optimal': os.path.join(script_dir, 'optimal_assignment_02.csv')
    },
    '03': {
        'greedy': os.path.join(script_dir, 'greedy_assignments-03.csv'),
        'optimal': os.path.join(script_dir, 'optimal_assignment_03.csv')
    }
}


# Function to compare the average service time and delivery cost for a single instance
def compare_instance(instance_number, greedy_path, optimal_path):
    try:
        # Load the greedy and optimal assignment files for this instance
        greedy_assignments = pd.read_csv(greedy_path)
        optimal_assignments = pd.read_csv(optimal_path)

        # Calculate the average service time and delivery cost for both methods
        greedy_avg_service_time = greedy_assignments['service_time'].mean()
        greedy_avg_cost = greedy_assignments['delivery_cost'].mean()

        optimal_avg_service_time = optimal_assignments['service_time'].mean()
        optimal_avg_cost = optimal_assignments['delivery_cost'].mean()

        # Display the results for this instance
        print(f"\nComparison for Instance {instance_number}:")
        print(
            f"Greedy Method - Average Service Time: {greedy_avg_service_time}, Average Delivery Cost: {greedy_avg_cost}")
        print(
            f"Optimal Method - Average Service Time: {optimal_avg_service_time}, Average Delivery Cost: {optimal_avg_cost}")

    except FileNotFoundError as e:
        print(f"Error: {e}. Please make sure the files exist at the specified path for instance {instance_number}.")
    except Exception as e:
        print(f"An unexpected error occurred in instance {instance_number}: {e}")


# Compare each instance separately
for instance_number, paths_dict in paths.items():
    print(f"Processing Instance {instance_number}...")
    compare_instance(instance_number, paths_dict['greedy'], paths_dict['optimal'])
