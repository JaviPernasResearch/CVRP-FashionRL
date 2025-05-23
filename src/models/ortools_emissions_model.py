from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from src.models.ortools_model import ORToolsModel

class ORToolsEmissionsModel(ORToolsModel):
    """CVRP solver implementation using Google OR-Tools optimizing for CO2 emissions"""
    
    def __init__(self, instance=None):
        super().__init__(instance=instance)
        self.name = 'fashion_reverse_logistics_ortools_emissions'
        # Default emission parameters if not provided in instance
        self.alpha = instance.get('alpha', 0.15)  # Base CO2 per km (kg/km)
        self.beta = instance.get('beta', 0.02)    # Load-dependent factor (kg/km/kg)
    
    def build_model(self):
        """Build the OR-Tools routing model with emissions-aware objective"""
        if not self.instance:
            raise ValueError("No instance data provided")
            
        # Extract instance data
        N = list(self.instance['N'])
        V = list(self.instance['V'])
        q = self.instance['q']  # Demands
        
        # Create the routing index manager
        self.manager = pywrapcp.RoutingIndexManager(len(V), len(N), 0)
        
        # Create Routing Model
        self.routing = pywrapcp.RoutingModel(self.manager)
        
        # Register distance callback
        def distance_callback(from_index, to_index):
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            return int(self.instance['c'].get((from_node, to_node), 0) * 100)  # Scale distances
        
        transit_callback_index = self.routing.RegisterTransitCallback(distance_callback)
        
        # Add capacity dimension for load tracking
        def demand_callback(from_index):
            from_node = self.manager.IndexToNode(from_index)
            return self.instance['q'].get(from_node, 0)
        
        demand_callback_index = self.routing.RegisterUnaryTransitCallback(demand_callback)
        capacity_dimension_name = 'Capacity'
        
        self.routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            [self.instance['Q']] * len(N),  # vehicle capacities
            True,  # start cumul to zero
            capacity_dimension_name)
            
        # Create emissions callback that depends on distance and load
        def emissions_callback(from_index, to_index):
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            
            # Get the distance between nodes
            distance = self.instance['c'].get((from_node, to_node), 0)
            
            # Calculate emissions based on distance and load
            # For emissions, we need the load at departure
            # This is calculated based on the remaining pickups after visiting from_node
            # Note: In OR-Tools, this callback is called before the dimension is fully set up,
            # so we estimate the load here based on a simple calculation
            
            # Base emissions (distance * alpha)
            base_emissions = distance * self.alpha
            
            # Estimate the vehicle load between nodes
            # For a reverse logistics problem, load increases as the vehicle progresses
            # Start with 0 at depot, add demand at each node
            load = 0
            if from_node != 0:  # If not starting at depot
                load = q.get(from_node, 0)  # Load collected at current node
            
            # Load-dependent emissions
            load_emissions = distance * self.beta * load
            
            # Total emissions
            total_emissions = (base_emissions + load_emissions) * 100  # Scale for integer math
            
            return int(total_emissions)
        
        # Register emissions callback
        emissions_callback_index = self.routing.RegisterTransitCallback(emissions_callback)
        
        # Set the cost function to emissions instead of just distance
        self.routing.SetArcCostEvaluatorOfAllVehicles(emissions_callback_index)
        
        # Add distance dimension for tracking and constraints
        distance_dimension_name = 'Distance'
        self.routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            1000000,  # large enough upper bound
            True,  # start cumul to zero
            distance_dimension_name)
        
        return self.routing
    
    def solve(self, time_limit=60, verbose=False):
        """Solve using OR-Tools with emissions-aware objective"""
        if not self.routing:
            self.build_model()
            
        # Setting search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        
        # Set local search metaheuristics
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        search_parameters.time_limit.seconds = time_limit
        search_parameters.log_search = verbose
        
        # Solve the problem
        if verbose:
            print("Solving with OR-Tools CP (Emissions-aware)...")
        
        self._stop_requested = False
        self._solving = True
        self.start_timer()
        
        or_solution = self.routing.SolveWithParameters(search_parameters)
        
        self.stop_timer()
        self._solving = False
        
        if or_solution:
            self.status = 2  # Solution found
            self.solution_count = 1
            self.objective_value = or_solution.ObjectiveValue() / 100  # Scale back
            
            # Extract routes from solution - same as parent class
            active_arcs = []
            
            for vehicle_id in range(len(self.instance['N'])):
                index = self.routing.Start(vehicle_id)
                route = []
                
                while not self.routing.IsEnd(index):
                    node_index = self.manager.IndexToNode(index)
                    route.append(node_index)
                    
                    previous_index = index
                    index = or_solution.Value(self.routing.NextVar(index))
                    next_node = self.manager.IndexToNode(index)
                    
                    # Add arc to solution
                    if not self.routing.IsEnd(index):  # Skip arcs to end depot
                        arc = (node_index, next_node)
                        active_arcs.append(arc)
                
                # Only consider non-empty routes
                if len(route) > 1:
                    # Add return to depot arc
                    active_arcs.append((route[-1], 0))
            
            # Update solution
            for arc in active_arcs:
                self.solution[arc] = 1
                
            # Add emissions info to instance for solution reporting
            self.instance['method_name'] = 'OR-Tools CP (Emissions-aware)'
            self.instance['alpha'] = self.alpha
            self.instance['beta'] = self.beta
            self.instance['emissions_optimized'] = True
            
            if verbose:
                self.print_solution_summary()
                
        else:
            if verbose:
                print("No solution found!")
            self.status = 3  # No solution
            
        return self.solution
    
    def print_solution_summary(self):
        """Print a summary of the solution with emissions information"""
        super().print_solution_summary()
        
        solution_obj = self.get_solution_object()
        routes = solution_obj.routes
        
        print("\nEmissions Parameters:")
        print(f"  Base CO2 per km (α): {self.alpha} kg/km")
        print(f"  Load-dependent factor (β): {self.beta} kg/km/kg")
        
        # Calculate total emissions
        total_emissions = 0
        print("\nEmissions by Route:")
        
        for route_id, route in routes.items():
            route_emissions = 0
            load = 0
            
            for i in range(len(route)-1):
                from_node = route[i]
                to_node = route[i+1]
                
                # Distance between nodes
                distance = self.instance['c'][(from_node, to_node)]
                
                # If not at depot, add the load from the node
                if from_node != 0:
                    load += self.instance['q'].get(from_node, 0)
                
                # Calculate emissions for this segment
                segment_emissions = distance * (self.alpha + self.beta * load)
                route_emissions += segment_emissions
            
            print(f"  Route {route_id}: {route_emissions:.2f} kg CO2")
            total_emissions += route_emissions
        
        print(f"\nTotal CO2 Emissions: {total_emissions:.2f} kg")