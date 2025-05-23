from src.models.model_factory import create_model
from src.utils.solution import Solution

def solve_cvrp(instance, method='exact', time_limit=60, **kwargs):
    """
    Solve a CVRP instance using the specified method.
    
    Parameters:
    ----------
    instance : dict
        Problem instance data
    method : str
        Solving method ('exact', 'heuristic', 'ortools')
    time_limit : int
        Maximum solution time in seconds
    **kwargs : dict
        Additional parameters for specific solvers
        
    Returns:
    -------
    Solution
        Solution object containing arcs and methods for analysis and visualization
    """
    verbose = kwargs.get('verbose', True)
    
    if verbose:
        print(f"Solving CVRP with {method} method, time limit: {time_limit}s")
    
    # Create model using factory
    model = create_model(method, instance)
    
    # Solve the model
    model.solve(time_limit=time_limit, verbose=verbose, **kwargs)
    
    if verbose:
        model.print_solution_summary()
    
    # Return solution object instead of just the arcs
    return Solution(instance, model.solution)