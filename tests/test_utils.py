import os
import pytest
import matplotlib.pyplot as plt
from src.data.data_handling import create_random_instance
from src.utils.visualization import plot_solution
from src.utils.analysis import analyze_solution

class TestUtils:
    
    @pytest.fixture
    def test_instance_and_solution(self):
        """Create a test instance and a simple solution"""
        instance = create_random_instance(5, 50, 10, seed=42)
        
        # Create a simple solution (two routes)
        solution = {
            (0, 1): 1, (1, 2): 1, (2, 0): 1,  # Route 1: 0 -> 1 -> 2 -> 0
            (0, 3): 1, (3, 4): 1, (4, 5): 1, (5, 0): 1  # Route 2: 0 -> 3 -> 4 -> 5 -> 0
        }
        
        return instance, solution
    
    def test_analyze_solution(self, test_instance_and_solution):
        """Test the solution analysis function"""
        instance, solution = test_instance_and_solution
        
        analysis = analyze_solution(instance, solution)
        
        # Check if analysis has the expected structure
        assert 'num_routes' in analysis
        assert 'total_distance' in analysis
        assert 'routes' in analysis
        
        # Check if there are 2 routes as expected
        assert analysis['num_routes'] == 2
        
        # Check if routes have the correct structure
        for route in analysis['routes']:
            assert 'sequence' in route
            assert 'distance' in route
            assert 'load' in route
            assert 'num_shops' in route
    
    def test_plot_solution(self, test_instance_and_solution, tmp_path):
        """Test the solution visualization function"""
        instance, solution = test_instance_and_solution
        output_path = os.path.join(tmp_path, "test_solution.png")
        
        # Close any existing plots
        plt.close('all')
        
        # Plot the solution
        plot_solution(instance, solution, output_path)
        
        # Check if the file exists
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0  # File should not be empty