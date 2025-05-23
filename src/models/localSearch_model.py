import time
import numpy as np
from numpy.random import RandomState
from src.models.base_model import CVRPModel

class localSearch_model(CVRPModel):
    """CVRP solver implementation using Iterated Local Search heuristic"""
    
    def __init__(self, instance=None):
        super().__init__(name='fashion_reverse_logistics_heuristic', instance=instance)
        self.best_routes = {}
        self.best_cost = float('inf')
        self.rand_gen = None
    
    def build_model(self):
        """Prepare the model (mostly a placeholder for consistency)"""
        if not self.instance:
            raise ValueError("No instance data provided")
        return self
    
    def solve(self, time_limit=60, iterations=100, random_state=None, verbose=False):
        """Solve using Iterated Local Search heuristic"""
        self._stop_requested = False
        self._solving = True
        self.start_timer()
        self.rand_gen = RandomState(random_state)
        
        if verbose:
            print(f"Starting heuristic solver with max {iterations} iterations and {time_limit}s time limit")
        
        # Extract instance data
        N = list(self.instance['N'])
        V = self.instance['V']
        c = self.instance['c']
        Q = self.instance['Q']
        q = self.instance['q']
        
        # Initialize solution using nearest neighbor heuristic
        tour = self._construct_initial_tour(N, c, self.rand_gen)
        current_routes = self._split_tour_into_routes(tour, Q, q)
        current_cost = self._calculate_solution_cost(current_routes, c)
        
        self.best_routes = current_routes.copy()
        self.best_cost = current_cost
        
        if verbose:
            print(f"Initial solution cost: {self.best_cost:.2f}")
            print(f"Initial number of routes: {len(self.best_routes)}")
        
        # Iterated Local Search
        iteration = 0
        no_improvement = 0
        while iteration < iterations and (not self.start_time or time.time() - self.start_time < time_limit):
            # Check if stop requested
            if self.should_stop():
                if verbose:
                    print("Stop requested. Terminating optimization...")
                break
                
            iteration += 1
            
            # Perturb current solution
            perturbed_tour = self._perturb_solution(tour, N, self.rand_gen)
            perturbed_routes = self._split_tour_into_routes(perturbed_tour, Q, q)
            
            # Apply 2-opt local search
            improved_tour = self._apply_2opt(perturbed_tour, c, Q, q, self.rand_gen)
            improved_routes = self._split_tour_into_routes(improved_tour, Q, q)
            improved_cost = self._calculate_solution_cost(improved_routes, c)
            
            # Update current solution
            if improved_cost < current_cost:
                tour = improved_tour
                current_routes = improved_routes
                current_cost = improved_cost
                no_improvement = 0
                
                # Update best solution if improved
                if improved_cost < self.best_cost:
                    self.best_routes = improved_routes.copy()
                    self.best_cost = improved_cost
                    if verbose:
                        print(f"Iteration {iteration}: New best solution with cost {self.best_cost:.2f}, routes: {len(self.best_routes)}")
            else:
                # Accept worse solution with small probability (for diversification)
                if self.rand_gen.random() < 0.1:
                    tour = improved_tour
                    current_routes = improved_routes
                    current_cost = improved_cost
                    if verbose:
                        print(f"Iteration {iteration}: Accepted worse solution for diversification")
                    
                no_improvement += 1
            
            # Restart if no improvement for a while
            if no_improvement >= 20:
                if verbose:
                    print(f"Iteration {iteration}: Restarting search due to lack of improvement")
                tour = self._construct_initial_tour(N, c, self.rand_gen)
                current_routes = self._split_tour_into_routes(tour, Q, q)
                current_cost = self._calculate_solution_cost(current_routes, c)
                no_improvement = 0
                
            if verbose and iteration % 10 == 0:
                elapsed = time.time() - self.start_time if self.start_time else 0
                print(f"Iteration {iteration}: Current best cost = {self.best_cost:.2f}, Elapsed time: {elapsed:.2f}s")
        
        # Update solution and model status
        self.solution = self._routes_to_arcs(self.best_routes)
        self.objective_value = self.best_cost
        self.solution_count = 1
        self.status = 2  # Solution found
        self.stop_timer()
        self._solving = False
        
        if verbose:
            print(f"\nHeuristic solution completed:")
            print(f"Final solution cost: {self.best_cost:.2f}")
            print(f"Number of routes: {len(self.best_routes)}")
            print(f"Solver running time: {self.runtime:.2f} seconds")
            print(f"Number of iterations: {iteration}")
        
        return self.solution
        
    def _construct_initial_tour(self, nodes, costs, rand_gen):
        """
        Construct an initial tour using nearest neighbor heuristic
        with a random starting node for diversification
        """
        remaining_nodes = nodes.copy()
        
        # Start from a random node
        if rand_gen.random() < 0.5:  # Sometimes start from depot
            current = 0
            tour = [0]
        else:  # Sometimes start from random node
            start_idx = rand_gen.randint(0, len(remaining_nodes))
            current = remaining_nodes[start_idx]
            remaining_nodes.remove(current)
            tour = [0, current]  # Always start at depot in the solution
        
        # Build tour using nearest neighbor heuristic
        while remaining_nodes:
            best_node = None
            best_cost = float('inf')
            
            for node in remaining_nodes:
                cost = costs.get((current, node), float('inf'))
                if cost < best_cost:
                    best_cost = cost
                    best_node = node
                    
            tour.append(best_node)
            current = best_node
            remaining_nodes.remove(best_node)
        
        return tour

    def _split_tour_into_routes(self, tour, capacity, demands):
        """Split a TSP tour into feasible CVRP routes respecting capacity constraints"""
        routes = {}
        route_idx = 1
        current_route = [0]  # Start at depot
        current_load = 0
        
        for node in tour:
            if node == 0:  # Skip depot in tour
                continue
                
            node_demand = demands.get(node, 0)
            
            # If adding this node exceeds capacity, close current route and start new one
            if current_load + node_demand > capacity:
                current_route.append(0)  # Return to depot
                routes[route_idx] = current_route
                route_idx += 1
                
                current_route = [0, node]  # Start new route
                current_load = node_demand
            else:
                current_route.append(node)
                current_load += node_demand
        
        # Close last route if not empty
        if len(current_route) > 1:
            current_route.append(0)  # Return to depot
            routes[route_idx] = current_route
            
        return routes

    def _calculate_solution_cost(self, routes, costs):
        """Calculate total cost of a solution"""
        total_cost = 0
        
        for _, route in routes.items():
            for i in range(len(route) - 1):
                from_node, to_node = route[i], route[i + 1]
                total_cost += costs.get((from_node, to_node), 0)
        
        return total_cost

    def _perturb_solution(self, tour, nodes, rand_gen):
        """Perturb the solution using random moves"""
        perturbed = tour.copy()
        n = len(perturbed)
        
        # Choose perturbation type
        perturbation_type = rand_gen.randint(0, 3)
        
        if perturbation_type == 0:
            # Random swaps (excluding depot)
            num_swaps = max(1, int(n * 0.2))  # Swap 20% of nodes
            for _ in range(num_swaps):
                i = rand_gen.randint(1, n)
                j = rand_gen.randint(1, n)
                if i < n and j < n:  # Ensure valid indices
                    perturbed[i], perturbed[j] = perturbed[j], perturbed[i]
                    
        elif perturbation_type == 1:
            # Random reversal of a segment
            if n > 3:
                i = rand_gen.randint(1, n-2)
                j = rand_gen.randint(i+1, n-1)
                perturbed[i:j+1] = reversed(perturbed[i:j+1])
                
        elif perturbation_type == 2:
            # Random insertion (move a node to another position)
            if n > 2:
                i = rand_gen.randint(1, n-1)
                j = rand_gen.randint(1, n-1)
                if i != j:
                    node = perturbed.pop(i)
                    perturbed.insert(j, node)
                    
        else:
            # Shuffle a segment
            if n > 3:
                i = rand_gen.randint(1, n-2)
                j = rand_gen.randint(i+1, n-1)
                segment = perturbed[i:j+1]
                rand_gen.shuffle(segment)
                perturbed[i:j+1] = segment
                
        return perturbed

    def _apply_2opt(self, tour, costs, capacity, demands, rand_gen):
        """Apply 2-opt local search to improve tour"""
        improved = True
        best_tour = tour.copy()
        best_cost = self._calculate_solution_cost(self._split_tour_into_routes(best_tour, capacity, demands), costs)
        max_iterations = min(len(tour) * 2, 100)  # Limit iterations for larger problems
        
        iteration = 0
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            # Try a sample of possible 2-opt moves for efficiency
            # For large problems, checking all pairs would be too time-consuming
            num_attempts = min(50, len(tour) * (len(tour) - 1) // 4)
            
            for _ in range(num_attempts):
                # Randomly select two positions (excluding depot)
                i = rand_gen.randint(1, len(tour) - 2)
                j = rand_gen.randint(i + 1, len(tour) - 1)
                
                # Apply 2-opt: reverse subpath from i to j
                new_tour = best_tour.copy()
                new_tour[i:j+1] = reversed(best_tour[i:j+1])
                
                # Check if better
                new_routes = self._split_tour_into_routes(new_tour, capacity, demands)
                new_cost = self._calculate_solution_cost(new_routes, costs)
                
                if new_cost < best_cost:
                    best_tour = new_tour
                    best_cost = new_cost
                    improved = True
                    break
        
        return best_tour

    def _routes_to_arcs(self, routes):
        """Convert routes to dictionary of active arcs"""
        active_arcs = {}  # Change to dictionary
        for _, route in routes.items():
            for i in range(len(route) - 1):
                active_arcs[(route[i], route[i+1])] = 1  # Store as {(i,j): 1}
        
        return active_arcs