import os
import pytest
import numpy as np
from src.data.data_handling import create_random_instance, load_instance, save_instance

class TestDataHandling:
    
    def test_create_random_instance(self):
        """Test creating a random CVRP instance"""
        instance = create_random_instance(10, 100, 20)
        
        # Check if all required keys are present
        assert 'N' in instance
        assert 'V' in instance
        assert 'A' in instance
        assert 'c' in instance
        assert 'Q' in instance
        assert 'q' in instance
        assert 'x_coords' in instance
        assert 'y_coords' in instance
        
        # Check correct dimensions
        assert len(instance['N']) == 10
        assert len(instance['V']) == 11  # Including depot
        assert len(instance['q']) == 11  # Including depot with demand 0
        assert instance['Q'] == 100
        
    def test_save_and_load_instance(self, tmp_path):
        """Test saving and loading an instance"""
        # Create a simple instance
        instance = create_random_instance(5, 50, 10)
        
        # Save it
        file_path = os.path.join(tmp_path, "test_instance.json")
        save_instance(instance, file_path)
        
        # Check if file exists
        assert os.path.exists(file_path)
        
        # Load it back
        loaded_instance = load_instance(file_path)
        
        # Check if loaded instance has same structure
        assert loaded_instance['N'] == instance['N']
        assert loaded_instance['V'] == instance['V']
        assert loaded_instance['Q'] == instance['Q']
        
        # Check if arrays are equal
        assert np.array_equal(loaded_instance['q'], instance['q'])
        assert np.array_equal(loaded_instance['x_coords'], instance['x_coords'])
        assert np.array_equal(loaded_instance['y_coords'], instance['y_coords'])