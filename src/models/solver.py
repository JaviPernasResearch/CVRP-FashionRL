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
        Solving method ('exact', 'heuristic', 'ortools', 'ortools_emissions')
    time_limit : int
        Maximum solution time in seconds
    **kwargs : dict
        Additional parameters for specific solvers:
        - iterations: for heuristic methods
        - alpha: base CO2 per km (kg/km) for emissions calculations
        - beta: load-dependent emission factor (kg/km/kg) for emissions calculations
        
    Returns:
    -------
    Solution
        Solution object containing arcs and methods for analysis and visualization
    """
    verbose = kwargs.get('verbose', True)
    
    if verbose:
        if method == 'ortools_emissions':
            alpha = instance.get('alpha', 0.15)
            beta = instance.get('beta', 0.02)
            print(f"Solving CVRP with {method} method, time limit: {time_limit}s")
            print(f"Emissions parameters: α={alpha} kg/km, β={beta} kg/km/kg")
        else:
            print(f"Solving CVRP with {method} method, time limit: {time_limit}s")
    
    # Store method name in instance for solution reporting
    instance['method_name'] = {
        'exact': 'Exact (Gurobi)',
        'heuristic': 'Heuristic (ILS)',
        'ortools': 'OR-Tools CP',
        'ortools_emissions': 'OR-Tools CP (Emissions)'
    }.get(method, method)
    
    # Create model using factory
    model = create_model(method, instance)
    
    # Solve the model
    model.solve(time_limit=time_limit, verbose=verbose, **kwargs)
    
    # Flag for solution object to know if this was emissions-optimized
    if method == 'ortools_emissions':
        instance['emissions_optimized'] = True
    
    if verbose:
        model.print_solution_summary()
    
    # Return solution object instead of just the arcs
    return Solution(instance, model.solution)