import os
from flow import create_flow


def main():
    """Run the nested batch example."""
    print("Processing school grades...\n")
    print("Note: Ensure you have grade files in the school/ directory structure.")
    
    # Create and run flow
    flow = create_flow()
    flow.run({})

if __name__ == "__main__":
    main() 