from datetime import datetime
import os

class Solution:
    """
    A class to represent and manipulate CVRP solutions.
    
    This encapsulates the solution representation and provides methods
    for analyzing routes, calculating metrics, and visualizing solutions.
    """
    
    def __init__(self, instance, arcs=None):
        """
        Initialize a solution object.
        
        Parameters:
        ----------
        instance : dict
            The problem instance data
        arcs : dict
            Dictionary of active arcs {(i,j): 1 if arc used, 0 otherwise}
        """
        self.instance = instance
        self.arcs = arcs or {}
        self._routes = None  # Cache for routes
        self._metrics = None  # Cache for solution metrics
    
    @property
    def active_arcs(self):
        """Get list of active arcs in the solution"""
        return [(i, j) for (i, j), val in self.arcs.items() if val > 0.5]
    
    @property
    def routes(self):
        """Extract and cache routes from solution arcs"""
        if self._routes is None:
            self._extract_routes()
        return self._routes
    
    @property
    def metrics(self):
        """Calculate and cache solution metrics"""
        if self._metrics is None:
            self._calculate_metrics()
        return self._metrics
    
    def _extract_routes(self):
        """Extract routes from solution arcs"""
        self._routes = {}
        active_arcs = self.active_arcs
        current_route_id = 1
        remaining_arcs = active_arcs.copy()
        
        while remaining_arcs:
            # Start at depot
            current_node = 0
            route = [current_node]
            
            # Follow arcs until returning to depot
            while current_node != 0 or len(route) == 1:
                found_next = False
                for i, (from_node, to_node) in enumerate(remaining_arcs):
                    if from_node == current_node:
                        route.append(to_node)
                        current_node = to_node
                        remaining_arcs.pop(i)
                        found_next = True
                        break
                
                if not found_next and current_node != 0:
                    # If no outgoing arc found, return to depot
                    route.append(0)
                    break
                    
            if len(route) > 2:  # Only include routes that visit at least one customer
                self._routes[current_route_id] = route
                current_route_id += 1
        
        return self._routes
    
    def _calculate_metrics(self):
        """Calculate solution metrics"""
        # Get problem parameters
        c = self.instance['c']  # Cost/distance matrix
        q = self.instance['q']  # Demand
        Q = self.instance['Q']  # Capacity
        
        route_details = []
        total_distance = 0
        
        for route_id, route in self.routes.items():
            route_distance = sum(c[route[i], route[i+1]] for i in range(len(route)-1))
            route_load = sum(q.get(node, 0) for node in route[1:-1])  # Skip depot
            
            route_details.append({
                'route_id': route_id,
                'sequence': route,
                'distance': route_distance,
                'load': route_load,
                'capacity': Q,
                'num_shops': len(route) - 2  # -2 to exclude depot at start and end
            })
            
            total_distance += route_distance
        
        self._metrics = {
            'total_distance': total_distance,
            'num_routes': len(self.routes),
            'routes': route_details
        }
        
        return self._metrics
    
    def save_solution_files(self, csv_file='reverse_logistics_solution.csv', 
                           details_file='solution_details.txt'):
        """Save solution to CSV and details to text file"""
        import pandas as pd
        
        result_folder = self.get_result_folder()  
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update file paths to use the results folder
        csv_path = os.path.join(result_folder, csv_file)
        details_path = os.path.join(result_folder, details_file)

        # Save solution to CSV
        solution_df = pd.DataFrame(self.active_arcs, columns=['from', 'to'])
        solution_df.to_csv(csv_path, index=False)
        
        # Save route details to text file
        with open(details_path, 'w', encoding='utf-8') as f:
            f.write("FASHION REVERSE LOGISTICS SOLUTION ANALYSIS\n")
            f.write("=========================================\n")
            f.write(f"Solver: {self.instance.get('method_name', 'Unknown Method')}\n")
            f.write(f"Generated on: {timestamp} \n")
            f.write(f"Problem size: {len(self.instance['N'])} shops\n")
            f.write(f"Vehicle capacity: {self.instance['Q']} units\n\n")
            
            f.write(f"Number of routes: {self.metrics['num_routes']}\n")
            f.write(f"Total distance: {self.metrics['total_distance']:.2f} units\n\n")

            # Calculate and print emissions if requested
            emissions_info = self.calculate_emissions()
            f.write(f"Estimated CO2 emissions: {emissions_info['total_emissions']:.2f} kg")

            # Show detailed emissions info if solution was emissions-optimized
            if self.instance.get('emissions_optimized', False):
                f.write(f"Emissions parameters: \u03B1={emissions_info['alpha']} kg/km, \u03B2={emissions_info['beta']} kg/km/kg")
            
            for route_data in self.metrics['routes']:
                route = route_data['sequence']
                route_id = route_data['route_id']
                
                f.write(f"\nRoute {route_id}:")
                f.write(f"  Sequence: {' -> '.join(map(str, route))}")
                f.write(f"  Distance: {route_data['distance']:.2f} units")
                f.write(f"  Load: {route_data['load']} / {route_data['capacity']} units")
                f.write(f"  Shops visited: {route_data['num_shops']}")

                # Add emissions info if available
                if emissions_info['route_emissions'] and route_id in emissions_info['route_emissions']:
                    f.write(f"  CO2 emissions: {emissions_info['route_emissions'][route_id]:.2f} kg")
        
        print(f"\nSolution saved to '{csv_path}'")
        print(f"Solution details saved to '{details_path}'")
        
        # Return the folder name for later reference
        return result_folder
    
    def calculate_emissions(self, alpha=0.15, beta=0.02):
        """
        Calculate CO2 emissions for the solution.
        
        Parameters:
        ----------
        alpha : float
            Base CO2 per km (kg/km)
        beta : float
            Load-dependent emission factor (kg/km/kg)
        
        Returns:
        -------
        dict
            Dictionary with emissions metrics
        """
        # Use instance-specific emission parameters if available
        alpha = self.instance.get('alpha', alpha)
        beta = self.instance.get('beta', beta)
        
        # Get problem parameters
        c = self.instance['c']  # Cost/distance matrix
        q = self.instance['q']  # Demand
        
        route_emissions = {}
        total_emissions = 0
        
        for route_id, route in self.routes.items():
            current_load = 0
            route_emission = 0
            
            for i in range(len(route)-1):
                from_node = route[i]
                to_node = route[i+1]
                
                # Distance between nodes
                distance = c[(from_node, to_node)]
                
                # If not at depot, add load from this node
                # For reverse logistics, we pick up at each node
                if from_node != 0:
                    current_load += q.get(from_node, 0)
                
                # Calculate emissions for this segment
                # Base emissions + load-dependent emissions
                segment_emissions = distance * (alpha + beta * current_load)
                route_emission += segment_emissions
            
            route_emissions[route_id] = route_emission
            total_emissions += route_emission
        
        return {
            'total_emissions': total_emissions,
            'route_emissions': route_emissions,
            'alpha': alpha,
            'beta': beta
        }
    
    def print_summary(self):
        """Print a summary of the solution"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        method_name = self.instance.get('method_name', 'Unknown Method')
        
        print("\nFASHION REVERSE LOGISTICS SOLUTION ANALYSIS")
        print("=========================================")
        print(f"Solver: {method_name}")
        print(f"Generated on: {timestamp}")
        print(f"Problem size: {len(self.instance['N'])} shops")
        print(f"Vehicle capacity: {self.instance['Q']} units\n")
        
        print(f"Number of routes: {self.metrics['num_routes']}")
        print(f"Total distance: {self.metrics['total_distance']:.2f} units")
        
        # Calculate and print emissions if requested
        emissions_info = self.calculate_emissions()
        print(f"Estimated CO2 emissions: {emissions_info['total_emissions']:.2f} kg")
        
        # Show detailed emissions info if solution was emissions-optimized
        if self.instance.get('emissions_optimized', False):
            print(f"Emissions parameters: α={emissions_info['alpha']} kg/km, β={emissions_info['beta']} kg/km/kg")
        
        for route_data in self.metrics['routes']:
            route = route_data['sequence']
            route_id = route_data['route_id']
            
            print(f"\nRoute {route_id}:")
            print(f"  Sequence: {' -> '.join(map(str, route))}")
            print(f"  Distance: {route_data['distance']:.2f} units")
            print(f"  Load: {route_data['load']} / {route_data['capacity']} units")
            print(f"  Shops visited: {route_data['num_shops']}")
            
            # Add emissions info if available
            if emissions_info['route_emissions'] and route_id in emissions_info['route_emissions']:
                print(f"  CO2 emissions: {emissions_info['route_emissions'][route_id]:.2f} kg")
    
    def visualize(self, output_file=None):
        """
        Visualize the solution
        
        Parameters:
        ----------
        output_file : str
            Path to save the visualization
        """
        import matplotlib.pyplot as plt
        import numpy as np
        from datetime import datetime
        
        plt.figure(figsize=(12, 8))
        
        # Get coordinates
        xc = self.instance['x_coords']
        yc = self.instance['y_coords']
        
        # Get current date and time for traceability
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        method_name = self.instance.get('method_name', 'Unknown Method')
        
        # Plot depot as a red square
        plt.plot(xc[0], yc[0], 'rs', markersize=10, label='Depot')
        
        # Plot shops as blue circles
        plt.scatter(xc[1:], yc[1:], c='blue', marker='o', s=50, label='Shops')
        
        # Add shop numbers
        for i in range(1, len(xc)):
            plt.annotate(str(i), (xc[i], yc[i]), xytext=(5, 5), textcoords='offset points')
        
        # Plot each route with different colors
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.routes)))
        
        for route_idx, (route_num, route) in enumerate(self.routes.items()):
            # Plot connections between consecutive points in route
            for i in range(len(route)-1):
                from_node = route[i]
                to_node = route[i+1]
                
                plt.plot([xc[from_node], xc[to_node]], [yc[from_node], yc[to_node]], 
                         c=colors[route_idx], linewidth=2)
                
                # Add arrows to indicate direction
                dx = xc[to_node] - xc[from_node]
                dy = yc[to_node] - yc[from_node]
                plt.arrow(xc[from_node] + 0.8*dx, yc[from_node] + 0.8*dy, 0.1*dx, 0.1*dy, 
                        head_width=3, head_length=3, fc=colors[route_idx], ec=colors[route_idx])
            
            # Add route to legend
            plt.plot([], [], c=colors[route_idx], label=f'Route {route_num}')
        
        # Set up the main title with solution info
        plt.title(f'Fashion Reverse Logistics Solution\n{method_name} | {timestamp}\n'
                 f'Shops: {len(self.instance["N"])} | Total Distance: {self.metrics["total_distance"]:.2f} | Routes: {self.metrics["num_routes"]}',
                 fontsize=12)
        
        plt.xlabel('X coordinate')
        plt.ylabel('Y coordinate')
        plt.legend()
        plt.grid(True)
        
        # Add additional solution info as text in the bottom right
        info_text = f"Total distance: {self.metrics['total_distance']:.2f}\n"
        info_text += f"Number of routes: {self.metrics['num_routes']}\n"
        info_text += f"Vehicle capacity: {self.instance['Q']} units"
        
        plt.figtext(0.95, 0.01, info_text, horizontalalignment='right', 
                   verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        if output_file:
            # If output_file contains no directory, use a results folder
            if not os.path.dirname(output_file):
                result_folder = self.get_result_folder()  
                os.makedirs(result_folder, exist_ok=True)
                output_file = os.path.join(result_folder, output_file)
            
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Route visualization saved to '{output_file}'")
        
        plt.close()
    
    def get_result_folder(self):
        """
        Get the results folder path for saving solution files.
        
        Returns:
        -------
        str
            Path to the results folder
        """
        # Get current date and time for traceability
        timestamp = datetime.now().strftime("%Y%m%d")
        method_name = self.instance.get('method_name', 'Unknown Method')

        # Create a folder for results with timestamp
        result_folder = f"results\\results_{timestamp}_{method_name}"
        os.makedirs(result_folder, exist_ok=True)

        return result_folder