import pytest
from src.data.data_handling import create_random_instance
from src.models.gurobi_model import solve_cvrp
from src.models.heuristic_model import solve_cvrp_heuristic
from src.models.ortools_model import solve_cvrp_ortools
from src.utils.analysis import analyze_solution

class TestModels:
    
    @pytest.fixture
    def small_instance(self):
        """Create a small test instance"""
        return create_random_instance(5, 50, 10, seed=42)
    
    def test_gurobi_model(self, small_instance):
        """Test the Gurobi solver on a small instance"""
        try:
            solution = solve_cvrp(small_instance, time_limit=60)
            
            # Check if solution exists
            assert solution is not None
            
            # Analyze solution
            analysis = analyze_solution(small_instance, solution)
            
            # Check basic properties
            assert analysis['total_distance'] > 0
            assert analysis['num_routes'] > 0
            
            # Check if all nodes are visited
            visited_nodes = set()
            for route in analysis['routes']:
                visited_nodes.update(route['sequence'][1:-1])  # Exclude depot
            assert visited_nodes == set(small_instance['N'])
            
        except ImportError:
            pytest.skip("Gurobi not installed")
    
    def test_heuristic_model(self, small_instance):
        """Test the heuristic solver on a small instance"""
        solution = solve_cvrp_heuristic(small_instance, iterations=100)
        
        # Check if solution exists
        assert solution is not None
        
        # Analyze solution
        analysis = analyze_solution(small_instance, solution)
        
        # Check if all nodes are visited
        visited_nodes = set()
        for route in analysis['routes']:
            visited_nodes.update(route['sequence'][1:-1])  # Exclude depot
        assert visited_nodes == set(small_instance['N'])
    
    def test_ortools_model(self, small_instance):
        """Test the OR-Tools solver on a small instance"""
        try:
            solution = solve_cvrp_ortools(small_instance, time_limit=60)
            
            # Check if solution exists
            assert solution is not None
            
            # Analyze solution
            analysis = analyze_solution(small_instance, solution)
            
            # Check if all nodes are visited
            visited_nodes = set()
            for route in analysis['routes']:
                visited_nodes.update(route['sequence'][1:-1])  # Exclude depot
            assert visited_nodes == set(small_instance['N'])
            
        except ImportError:
            pytest.skip("OR-Tools not installed")