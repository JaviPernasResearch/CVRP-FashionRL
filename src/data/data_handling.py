import os
import numpy as np
import pandas as pd

def load_problem_instance(file_path):
    '''
    Load a CVRP instance from a CSV file.
    
    Parameters:
    ------
    file_path: str
        Path to the CSV file containing problem data
    
    Returns:
    -----
        dict, keys = N, V, A, c, Q, q, x_coords, y_coords, alpha, beta
    '''
    try:
        # Read locations data
        locations_df = pd.read_csv(file_path)
        
        # Extract capacity and emissions parameters from metadata
        meta_params = {}
        with open(file_path.replace('.csv', '_meta.txt'), 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=')
                    meta_params[key] = float(value)
        
        vehicle_capacity = int(meta_params.get('capacity', 10))
        
        # Process locations data
        n_shops = len(locations_df) - 1  # Excluding depot
        
        # Extract coordinates
        x_coords = locations_df['x_coord'].values
        y_coords = locations_df['y_coord'].values
        
        # Extract demands
        demands = {}
        for i, demand in enumerate(locations_df['demand'].values):
            if i > 0:  # Skip depot
                demands[i] = demand
        
        # N is the set of shops (excluding depot)
        N = np.arange(1, n_shops+1)
        # V is the set of all locations (including depot at 0)
        V = np.arange(0, n_shops+1)
        # A is the set of all arcs
        A = [(i, j) for i in V for j in V if i != j]
        
        # c is the cost (distance) between locations
        c = {(i, j): np.hypot(x_coords[i]-x_coords[j], y_coords[i]-y_coords[j]) 
             for i, j in A}
        
        result = {
            'x_coords': x_coords, 
            'y_coords': y_coords,
            'N': N,
            'V': V, 
            'A': A, 
            'c': c, 
            'Q': vehicle_capacity, 
            'q': demands
        }
        
        # Add emissions parameters if available
        if 'alpha' in meta_params:
            result['alpha'] = meta_params['alpha']
        if 'beta' in meta_params:
            result['beta'] = meta_params['beta']
            
        return result
    
    except Exception as e:
        raise Exception(f"Error loading problem instance: {str(e)}")


def create_random_problem_instance(n_shops, vehicle_capacity, random_state=None):
    '''
    Create an instance of the CVRP for reverse logistics in fashion.
    
    Parameters:
    ------
    n_shops: int
        Number of shops to visit
    vehicle_capacity: int
        Capacity of each vehicle (in units)
    random_state: int, optional (default=None)
        Seed for reproducibility
    
    Returns:
    -----
        dict, keys = N, V, A, c, Q, q, x_coords, y_coords
    '''
    rand_gen = np.random.RandomState(seed=random_state)
    
    # Shop locations (randomly generated) + 1 for the depot
    x_coords = rand_gen.random(size=n_shops+1) * 200
    y_coords = rand_gen.random(size=n_shops+1) * 100
    
    # N is the set of shops (excluding depot)
    N = np.arange(1, n_shops+1)
    # V is the set of all locations (including depot at 0)
    V = np.arange(0, n_shops+1)
    # A is the set of all arcs
    A = [(i, j) for i in V for j in V if i != j]
    
    # c is the cost (distance) between locations
    c = {(i, j): np.hypot(x_coords[i]-x_coords[j], y_coords[i]-y_coords[j]) 
         for i, j in A}
    
    # Q is the vehicle capacity
    Q = vehicle_capacity
    
    # q is the demand at each shop (random number of items to pick up)
    q = {i: rand_gen.randint(1, 3) for i in N}  # Each shop has 1-3 units to return
    
    return {
        'x_coords': x_coords, 
        'y_coords': y_coords,
        'N': N,
        'V': V, 
        'A': A, 
        'c': c, 
        'Q': Q, 
        'q': q
    }


def add_emissions_parameters(instance, alpha=0.15, beta=0.02):
    """
    Add emissions parameters to an instance.
    
    Parameters:
    ----------
    instance : dict
        The problem instance to modify
    alpha : float
        Base CO2 per km (kg/km)
    beta : float
        Load-dependent emission factor (kg/km/kg)
    
    Returns:
    -------
    dict
        The modified instance with emissions parameters
    """
    instance['alpha'] = alpha
    instance['beta'] = beta
    return instance


def save_problem_instance(instance, output_path):
    '''
    Save a problem instance to a CSV file
    
    Parameters:
    ------
    instance: dict
        The problem instance to save
    output_path: str
        Path to save the CSV file
    '''
    try:
        # Create dataframe for locations
        data = {
            'id': range(len(instance['x_coords'])),
            'x_coord': instance['x_coords'],
            'y_coord': instance['y_coords'],
            'demand': [0] + [instance['q'].get(i, 0) for i in instance['N']]  # 0 demand for depot
        }
        
        locations_df = pd.DataFrame(data)
        
        # Save locations to CSV
        locations_df.to_csv(output_path, index=False)
        
        # Save metadata (vehicle capacity) to a separate text file
        with open(output_path.replace('.csv', '_meta.txt'), 'w') as f:
            f.write(f"capacity={instance['Q']}\n")
            
            # Add emissions parameters if they exist
            if 'alpha' in instance:
                f.write(f"alpha={instance['alpha']}\n")
            if 'beta' in instance:
                f.write(f"beta={instance['beta']}\n")
            
        print(f"Problem instance saved to {output_path}")
        
    except Exception as e:
        print(f"Error saving problem instance: {str(e)}")


def create_sample_instances():
    '''
    Create and save sample problem instances
    '''
    # Create directory if it doesn't exist
    os.makedirs('instances', exist_ok=True)
    
    # Small instance (10 shops)
    small_instance = create_random_problem_instance(n_shops=10, vehicle_capacity=10, random_state=42)
    add_emissions_parameters(small_instance)  # Add default emissions parameters
    save_problem_instance(small_instance, 'instances/small_instance.csv')
    
    # Medium instance (20 shops)
    medium_instance = create_random_problem_instance(n_shops=20, vehicle_capacity=15, random_state=43)
    add_emissions_parameters(medium_instance, alpha=0.18, beta=0.025)  # Different parameters
    save_problem_instance(medium_instance, 'instances/medium_instance.csv')
    
    # Large instance (50 shops)
    large_instance = create_random_problem_instance(n_shops=50, vehicle_capacity=20, random_state=44)
    add_emissions_parameters(large_instance, alpha=0.2, beta=0.03)  # Different parameters 
    save_problem_instance(large_instance, 'instances/large_instance.csv')
    
    print("Sample instances created in 'instances' directory")