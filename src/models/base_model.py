from abc import ABC, abstractmethod
import time
import threading
from src.utils.solution import Solution

class CVRPModel(ABC):
    """
    Abstract base class for all CVRP solver models.
    This standardizes the interface across different solver implementations.
    """
    
    def __init__(self, name='cvrp_model', instance=None):
        self.name = name
        self.instance = instance
        self.status = None
        self.solution_count = 0
        self.objective_value = float('inf')
        self.gap = None
        self.runtime = 0
        self.solution = {}  # Will store arc variables {(i,j): value}
        self.start_time = None
        self._stop_requested = False
        self._solve_thread = None
        self._solving = False
    
    @abstractmethod
    def build_model(self):
        """Build the optimization model with the given instance data"""
        pass
    
    @abstractmethod
    def solve(self, time_limit=60, **kwargs):
        """Solve the model with a given time limit"""
        pass
    
    def start_timer(self):
        """Start the solution timer"""
        self.start_time = time.time()
    
    def stop_timer(self):
        """Stop the solution timer and record runtime"""
        if self.start_time:
            self.runtime = time.time() - self.start_time
    
    def get_solution(self):
        """Return the current solution as a dictionary of arcs"""
        return self.solution
    
    def get_solution_object(self):
        """Return the current solution as a Solution object"""
        # Ensure instance has method name
        instance_copy = dict(self.instance) if self.instance else {}
        instance_copy['method_name'] = self.name
        
        return Solution(instance_copy, self.solution)
    
    def get_objective_value(self):
        """Return the objective value of the current solution"""
        return self.objective_value
    
    def get_runtime(self):
        """Return the solution runtime in seconds"""
        return self.runtime
    
    def is_solved(self):
        """Check if a solution has been found"""
        return self.solution_count > 0
    
    def is_solving(self):
        """Check if the model is currently solving"""
        return self._solving
        
    def request_stop(self):
        """Request to stop the optimization process"""
        self._stop_requested = True
        return True
        
    def should_stop(self):
        """Check if a stop has been requested"""
        return self._stop_requested
    
    def solve_async(self, callback=None, **kwargs):
        """
        Start solving in a background thread and call the callback when done
        
        Parameters:
        ----------
        callback : function
            Function to call when solving is complete, with the solution as argument
        **kwargs : dict
            Parameters to pass to the solve method
        """
        self._stop_requested = False
        self._solving = True
        
        def solve_thread_func():
            self.solve(**kwargs)  # This stores the solution in self.solution
            self._solving = False
            if callback:
                # Pass a Solution object to the callback, not just the arcs dictionary
                callback(Solution(self.instance, self.solution))
            return self.solution
        
        self._solve_thread = threading.Thread(target=solve_thread_func)
        self._solve_thread.daemon = True  # Thread will exit when main program exits
        self._solve_thread.start()
    
    def print_solution_summary(self):
        """Print a summary of the solution"""
        status_str = "Optimal" if self.status == 2 else "Feasible" if self.status == 1 else "Infeasible/Unknown"
        
        print(f"\n{self.name} Solution Summary:")
        print(f"Status: {status_str}")
        print(f"Objective Value: {self.objective_value:.2f}")
        print(f"Solution Time: {self.runtime:.2f} seconds")
        
        if self.gap is not None:
            print(f"Gap: {self.gap:.4f}")