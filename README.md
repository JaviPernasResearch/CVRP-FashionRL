# Fashion Reverse Logistics CVRP Solver

A user-friendly application for solving Capacitated Vehicle Routing Problems (CVRP) in fashion reverse logistics operations. This tool helps fashion retailers optimize their collection routes when picking up returns or unsold items from multiple store locations.

## Features

- **Multiple Solving Methods**:
  - Exact solution using Gurobi (mathematical optimization)
  - Heuristic solution using Iterated Local Search (fast approximation)
  - Constraint Programming with Google OR-Tools
- **User Interfaces**:
  - Graphical interface for interactive use
  - Command-line interface for batch processing
- **Solution Analysis**:
  - Visual route maps
  - Detailed metrics and statistics
  - Organized results with timestamps for traceability

## Quick Start Guide

### Installation

1. Make sure you have Python 3.8+ installed on your computer
2. Clone or download this repository
3. Open a command prompt/terminal in the project folder
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. For exact solving with Gurobi (optional):
   - Install Gurobi from [https://www.gurobi.com/downloads/](https://www.gurobi.com/downloads/)
   - Obtain and activate a license (free for academic use)

### Running the Application

**Using the Graphical Interface (recommended for beginners):**

```
python -m src.main --gui
```

**Using the Command Line:**

```
python -m src.main --file examples/small_instance.json --method heuristic
```

## User Guide for Non-Experts

### What This Tool Does

This application helps solve a common logistics problem: how to efficiently collect items from multiple shops using a fleet of vehicles with limited capacity. The goal is to find the shortest possible routes while ensuring each shop is visited exactly once and vehicle capacity isn't exceeded.

### Using the Graphical Interface

1. **Launch the GUI**:
   ```
   python -m src.main --gui
   ```

2. **Input Data Selection**:
   - **Option 1**: Load an existing problem file by clicking "Browse"
   - **Option 2**: Generate a random problem by checking "Generate random instance" and setting parameters:
     - Number of shops: How many pickup locations exist
     - Vehicle capacity: How many items each vehicle can carry
     - Random seed: Controls randomization (use the same seed to reproduce results)

3. **Solver Parameters**:
   - **Solution method**:
     - Exact (Gurobi): Best quality solutions but may be slow for large problems
     - Heuristic (ILS): Fast approximate solutions suitable for larger problems
     - CP (OR-Tools): Good compromise between quality and speed
   - **Time limit**: Maximum time (seconds) the solver will run
   - **Max iterations**: For heuristic method, how many improvement attempts to make

4. **Run the Solver**:
   - Click "Run Solver" to start optimization
   - The status area will show progress and results
   - You can stop the optimization early by clicking "Stop Solver" if needed

5. **Results**:
   - A summary appears in the status area when solving completes
   - A visualization image is saved showing all routes on a map
   - Detailed results are saved in a timestamped folder for later reference

### Using Sample Problems

Click "Create Sample Instances" to generate example problems. These are saved in the `examples` folder and can be loaded through the GUI's file browser.

### Understanding the Output

1. **Solution Summary**:
   - Number of routes required
   - Total distance traveled
   - Details of each route (shops visited, distance, load)

2. **Visualization**:
   - Depot shown as a red square
   - Shops shown as blue circles with numbers
   - Routes shown as colored lines with arrows showing direction
   - Legend identifies each route

3. **Output Files** (in a timestamped results folder):
   - PNG image showing the routes
   - CSV file with the solution data
   - TXT file with detailed solution analysis

### Command Line Usage

For advanced users or batch processing:

```
python -m src.main --file PATH_TO_FILE --method [exact/heuristic/ortools] --time-limit SECONDS
```

Additional options:
- `--shops N`: Number of shops (for random instances)
- `--capacity N`: Vehicle capacity (for random instances)
- `--seed N`: Random seed value (for reproducibility)
- `--iterations N`: Max iterations for heuristic method
- `--create-samples`: Generate sample problem instances

## Project Structure

```
CVRP-Andrea/
├── src/                      # Source code
│   ├── main.py               # Main entry point
│   ├── data/                 # Data handling
│   ├── models/               # Solver implementations
│   ├── ui/                   # User interfaces
│   └── utils/                # Utility functions
├── tests/                    # Unit tests
├── examples/                 # Example problem instances
├── results_*/                # Output directories for solutions
├── requirements.txt          # Dependencies
└── setup.py                  # Package configuration
```

## Troubleshooting

- **"No module named 'src'"**: Run the application from the project root directory
- **"No module named 'gurobipy'"**: Gurobi is not installed. Use heuristic or OR-Tools method instead
- **No solution found**: Try increasing the time limit or using a different method
- **Slow performance with large problems**: Use the heuristic method instead of the exact solver

## License

This project is licensed under the MIT License