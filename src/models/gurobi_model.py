from gurobipy import Model, GRB, quicksum
from src.models.base_model import CVRPModel

class GurobiModel(CVRPModel):
    """CVRP solver implementation using Gurobi"""
    
    def __init__(self, instance=None):
        super().__init__(name='fashion_reverse_logistics_gurobi', instance=instance)
        self.model = None
        self.x_vars = None
        self.u_vars = None
    
    def build_model(self):
        """Build the Gurobi optimization model"""
        if not self.instance:
            raise ValueError("No instance data provided")
        
        N = self.instance['N']
        V = self.instance['V']
        A = self.instance['A']
        c = self.instance['c']
        Q = self.instance['Q']
        q = self.instance['q']
        
        # Create new Gurobi model
        self.model = Model(self.name)
        
        # x[i,j] = 1 if vehicle travels from i to j, 0 otherwise
        self.x_vars = self.model.addVars(A, vtype=GRB.BINARY, name="x")
        
        # u[i] represents the cumulative load on the vehicle after visiting location i
        self.u_vars = self.model.addVars(N, vtype=GRB.CONTINUOUS, name="u")
        
        # Objective: minimize total distance
        self.model.modelSense = GRB.MINIMIZE
        self.model.setObjective(quicksum(self.x_vars[a] * c[a] for a in A))
        
        # Each shop must be visited exactly once
        self.model.addConstrs(quicksum(self.x_vars[i, j] for j in V if j != i) == 1 for i in N)
        self.model.addConstrs(quicksum(self.x_vars[i, j] for i in V if i != j) == 1 for j in N)
        
        # Load constraints with subtour elimination
        self.model.addConstrs((self.x_vars[i, j] == 1) >> (self.u_vars[i] + q[j] == self.u_vars[j])
                        for i, j in A if i != 0 and j != 0)
        
        # Load constraints
        self.model.addConstrs(self.u_vars[i] >= q[i] for i in N)
        self.model.addConstrs(self.u_vars[i] <= Q for i in N)
        
        return self.model
    
    def solve(self, time_limit=60, verbose=False):
        """Solve the model with Gurobi"""
        if not self.model:
            self.build_model()
        
        # Configure Gurobi parameters
        if not verbose:
            self.model.setParam('OutputFlag', 0)
        
        self.model.setParam('TimeLimit', time_limit)
        
        # Set up a callback function to check for stop requests
        def terminate_callback(model, where):
            if where == GRB.Callback.MIP:
                if self.should_stop():
                    if verbose:
                        print("Stop requested. Terminating optimization...")
                    model.terminate()
        
        # Solve the model and measure time
        self._stop_requested = False
        self._solving = True
        self.start_timer()
        
        try:
            self.model.optimize(terminate_callback)
        except Exception as e:
            if verbose:
                print(f"Error during optimization: {str(e)}")
        
        self.stop_timer()
        self._solving = False
        
        # Update solution information
        self.status = self.model.status
        self.solution_count = self.model.SolCount
        
        if self.model.SolCount > 0:
            self.objective_value = self.model.ObjVal
            self.gap = self.model.MIPGap
            
            # Extract solution
            for i, j in self.instance['A']:
                if self.x_vars[i, j].x > 0.5:  # Binary variable with value close to 1
                    self.solution[(i, j)] = 1
        
        return self.solution
