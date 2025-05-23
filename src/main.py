import os
import sys
# Add the project root to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse

# Import modules from our project
from src.data.data_handling import create_sample_instances
from src.ui.cli import run_cli
from src.ui.gui import run_gui

def main():
    parser = argparse.ArgumentParser(description='Solve Fashion Reverse Logistics CVRP')
    parser.add_argument('--gui', action='store_true', help='Launch the graphical user interface')
    parser.add_argument('--file', type=str, help='Path to problem instance file')
    parser.add_argument('--shops', type=int, default=10, help='Number of shops')
    parser.add_argument('--capacity', type=int, default=10, help='Vehicle capacity')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--time-limit', type=int, default=30, help='Solver time limit in seconds (default: 30)')
    parser.add_argument('--create-samples', action='store_true', help='Create sample instances')
    parser.add_argument('--method', type=str, choices=['exact', 'heuristic', 'ortools'], default='exact',
                       help='Solution method: exact (Gurobi), heuristic (ILS), or ortools (CP)')
    parser.add_argument('--iterations', type=int, default=100, help='Max iterations for heuristic method')
    args = parser.parse_args()
    
    # Create sample instances if requested
    if args.create_samples:
        create_sample_instances()
        return
        
    # Launch GUI if requested
    if args.gui:
        import sys
        run_gui()
        return
    
    # Run command line interface
    run_cli(args)


if __name__ == "__main__":
    main()