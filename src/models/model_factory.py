from src.models.gurobi_model import GurobiModel
from src.models.heuristic_model import HeuristicModel
from src.models.ortools_model import ORToolsModel

def create_model(model_type, instance=None):
    """
    Factory function to create the appropriate model instance.
    
    Parameters:
    ----------
    model_type : str
        Type of model to create ('exact', 'heuristic', 'ortools')
    instance : dict
        Problem instance data
        
    Returns:
    -------
    CVRPModel
        An instance of the requested model type
    """
    # Add method name to instance for traceability
    if instance is not None:
        instance = dict(instance)  # Create a copy to avoid modifying the original
        instance['method_name'] = model_type.capitalize()
    
    if model_type.lower() == 'exact':
        try:
            return GurobiModel(instance)
        except ImportError:
            print("Gurobi not available. Falling back to heuristic method.")
            if instance:
                instance['method_name'] = 'Heuristic (fallback)'
            return HeuristicModel(instance)
    
    elif model_type.lower() == 'heuristic':
        return HeuristicModel(instance)
    
    elif model_type.lower() == 'ortools':
        try:
            return ORToolsModel(instance)
        except ImportError:
            print("OR-Tools not available. Falling back to heuristic method.")
            return HeuristicModel(instance)
    
    else:
        raise ValueError(f"Unknown model type: {model_type}")