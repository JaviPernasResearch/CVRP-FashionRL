from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from src.models.base_model import CVRPModel

class ORToolsModel(CVRPModel):
    """CVRP solver implementation using Google OR-Tools"""
    
    def __init__(self, instance=None):
        super().__init__(name='fashion_reverse_logistics_ortools', instance=instance)
        self.manager = None
        self.routing = None
        self.solution = {}
    
    def build_model(self):
        """Build the OR-Tools routing model"""
        if not self.instance:
            raise ValueError("No instance data provided")
            
        # Extract instance data
        N = list(self.instance['N'])
        V = list(self.instance['V'])
        
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
        
        # Define cost of each arc
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Add Capacity constraint
        def demand_callback(from_index):
            from_node = self.manager.IndexToNode(from_index)
            return self.instance['q'].get(from_node, 0)
        
        demand_callback_index = self.routing.RegisterUnaryTransitCallback(demand_callback)
        self.routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            [self.instance['Q']] * len(N),  # vehicle capacities
            True,  # start cumul to zero
            'Capacity')
            
        return self.routing
    
    def solve(self, time_limit=60, verbose=False):
        """Solve using OR-Tools"""
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
        
        # OR-Tools doesn't have a direct way to stop the solver during execution
        # We'll have to rely on the time limit or completion
        
        # Solve the problem
        if verbose:
            print("Solving with OR-Tools CP...")
        
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
            
            # Extract routes from solution
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
                
            if verbose:
                self.print_solution_summary()
                
        else:
            if verbose:
                print("No solution found!")
            self.status = 3  # No solution
            
        return self.solution