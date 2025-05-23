import time
from gurobipy import GRB

# Import modules from our project
from src.data.data_handling import load_problem_instance, create_random_problem_instance
from src.models.solver import solve_cvrp

def run_cli(args):
    """Run the command line interface with given arguments"""
    # Load or create instance 
    if args.file:
        instance = load_problem_instance(args.file)
        print(f"Loaded problem instance from {args.file}")
    else:
        instance = create_random_problem_instance(args.shops, args.capacity, args.seed)
        print(f"Created random problem instance with {args.shops} shops")
    
    # Solve the instance
    solution = solve_cvrp(
        instance, 
        method=args.method,
        time_limit=args.time_limit,
        iterations=args.iterations,
        random_state=args.seed,
        verbose=True
    )
    
    # Print solution summary
    solution.print_summary()
    
    # Save solution files
    solution.save_solution_files()
    
    # Visualize solution
    solution.visualize("reverse_logistics_solution.png")