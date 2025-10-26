import os
from flow import create_flow

def main():
    """Run the batch processing example."""
    # Initialize shared store
    shared = {
        "input_file": "data/sales.csv"
    }
    
    # Check if data file exists
    if not os.path.exists(shared["input_file"]):
        print(f"Error: Data file {shared['input_file']} not found.")
        print("Please ensure you have a sales.csv file in the data/ directory.")
        return
    
    # Create and run flow
    print(f"Processing {shared['input_file']} in chunks...")
    flow = create_flow()
    flow.run(shared)

if __name__ == "__main__":
    main() 