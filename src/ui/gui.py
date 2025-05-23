import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import time

# Import modules from our project
from src.data.data_handling import load_problem_instance, create_random_problem_instance, create_sample_instances
from src.models.model_factory import create_model

class TextRedirector:
    """Redirects print output to a tkinter text widget"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        
    def write(self, string):
        self.text_widget.insert("end", string)
        self.text_widget.see("end")
        self.text_widget.update_idletasks()
        
    def flush(self):
        pass


class InputFrame:
    """Frame for handling input data selection"""
    def __init__(self, parent):
        self.parent = parent
        
        # Create the main frame
        self.frame = ttk.LabelFrame(parent, text="Input Data")
        self.frame.pack(fill="x", padx=10, pady=10)
        
        # Variables
        self.input_var = tk.StringVar()
        self.random_instance_var = tk.BooleanVar(value=False)
        self.shops_var = tk.StringVar(value="10")
        self.capacity_var = tk.StringVar(value="10")
        self.seed_var = tk.StringVar(value="42")
        
        # File input section
        self._create_file_input_section()
        
        # Random instance checkbox
        self._create_random_instance_section()
        
        # Random parameters frame (initially hidden)
        self.random_params_frame = ttk.Frame(self.frame)
        self._create_random_params_section()
    
    def _create_file_input_section(self):
        file_frame = ttk.Frame(self.frame)
        file_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(file_frame, text="Instance file:").pack(side="left", padx=5)
        self.input_entry = ttk.Entry(file_frame, textvariable=self.input_var, width=40)
        self.input_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        self.browse_button = ttk.Button(file_frame, text="Browse", command=self._browse_file)
        self.browse_button.pack(side="left", padx=5)
    
    def _create_random_instance_section(self):
        random_check = ttk.Checkbutton(
            self.frame, 
            text="Generate random instance", 
            variable=self.random_instance_var,
            command=self._toggle_random_instance
        )
        random_check.pack(anchor="w", padx=5, pady=5)
    
    def _create_random_params_section(self):
        # Number of shops
        param_frame1 = ttk.Frame(self.random_params_frame)
        param_frame1.pack(fill="x", pady=2)
        ttk.Label(param_frame1, text="Number of shops:").pack(side="left", padx=5)
        ttk.Entry(param_frame1, textvariable=self.shops_var, width=10).pack(side="left", padx=5)
        
        # Vehicle capacity
        param_frame2 = ttk.Frame(self.random_params_frame)
        param_frame2.pack(fill="x", pady=2)
        ttk.Label(param_frame2, text="Vehicle capacity:").pack(side="left", padx=5)
        ttk.Entry(param_frame2, textvariable=self.capacity_var, width=10).pack(side="left", padx=5)
        
        # Random seed
        param_frame3 = ttk.Frame(self.random_params_frame)
        param_frame3.pack(fill="x", pady=2)
        ttk.Label(param_frame3, text="Random seed:").pack(side="left", padx=5)
        ttk.Entry(param_frame3, textvariable=self.seed_var, width=10).pack(side="left", padx=5)
    
    def _browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Instance File",
            filetypes=[
                ("All supported files", "*.csv *.json *.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.input_var.set(filename)
    
    def _toggle_random_instance(self):
        if self.random_instance_var.get():
            self.random_params_frame.pack(fill="x", padx=10, pady=5)
            self.browse_button.config(state="disabled")
            self.input_entry.config(state="disabled")
        else:
            self.random_params_frame.pack_forget()
            self.browse_button.config(state="normal")
            self.input_entry.config(state="normal")
    
    def get_instance_data(self):
        """Returns the instance data based on user selection"""
        if self.random_instance_var.get():
            try:
                n_shops = int(self.shops_var.get())
                capacity = int(self.capacity_var.get())
                seed = int(self.seed_var.get())
                
                return {
                    'type': 'random',
                    'n_shops': n_shops,
                    'capacity': capacity,
                    'seed': seed
                }
            except ValueError:
                raise ValueError("All numerical inputs must be valid integers")
        else:
            file_path = self.input_var.get()
            if not file_path:
                raise ValueError("Please select an instance file")
            
            return {
                'type': 'file',
                'file_path': file_path
            }


class SolverFrame:
    """Frame for solver parameters"""
    def __init__(self, parent):
        self.parent = parent
        
        # Create the main frame
        self.frame = ttk.LabelFrame(parent, text="Solver Parameters")
        self.frame.pack(fill="x", padx=10, pady=10)
        
        # Solution method variable
        self.method_var = tk.StringVar(value="exact")
        
        # Method selection frame
        method_frame = ttk.Frame(self.frame)
        method_frame.pack(fill="x", pady=5)
        ttk.Label(method_frame, text="Solution method:").pack(side="left", padx=5)
        
        # Radio buttons for solution methods
        ttk.Radiobutton(
            method_frame, 
            text="Exact (Gurobi)", 
            variable=self.method_var, 
            value="exact",
            command=self._toggle_options
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            method_frame, 
            text="Heuristic (ILS)", 
            variable=self.method_var, 
            value="heuristic",
            command=self._toggle_options
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            method_frame, 
            text="CP (OR-Tools)", 
            variable=self.method_var, 
            value="ortools",
            command=self._toggle_options
        ).pack(side="left", padx=5)
        
        # Time limit variable
        self.time_limit_var = tk.StringVar(value="30")
        
        # Time limit entry
        time_frame = ttk.Frame(self.frame)
        time_frame.pack(fill="x", pady=5)
        ttk.Label(time_frame, text="Time limit (seconds):").pack(side="left", padx=5)
        ttk.Entry(time_frame, textvariable=self.time_limit_var, width=10).pack(side="left", padx=5)
        
        # Heuristic parameters
        self.iterations_var = tk.StringVar(value="100")
        self.heuristic_frame = ttk.Frame(self.frame)
        ttk.Label(self.heuristic_frame, text="Max iterations:").pack(side="left", padx=5)
        ttk.Entry(self.heuristic_frame, textvariable=self.iterations_var, width=10).pack(side="left", padx=5)
        
        # Initialize visibility based on selected method
        self._toggle_options()
    
    def _toggle_options(self):
        """Show/hide options based on selected method"""
        if self.method_var.get() == "heuristic":
            self.heuristic_frame.pack(fill="x", pady=5)
        else:
            self.heuristic_frame.pack_forget()
    
    def get_parameters(self):
        """Returns the solver parameters"""
        try:
            time_limit = int(self.time_limit_var.get())
            method = self.method_var.get()
            
            params = {
                'method': method,
                'time_limit': time_limit
            }
            
            if method == "heuristic":
                params['iterations'] = int(self.iterations_var.get())
            
            return params
        except ValueError:
            raise ValueError("All numerical inputs must be valid integers")


class StatusFrame:
    """Frame for displaying status and output"""
    def __init__(self, parent):
        self.parent = parent
        
        # Create the main frame
        self.frame = ttk.LabelFrame(parent, text="Status")
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Status text widget
        self.status_text = tk.Text(self.frame, height=10, wrap="word")
        self.status_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.status_text, orient="vertical", command=self.status_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Text redirector for capturing print output
        self.redirector = TextRedirector(self.status_text)
    
    def clear(self):
        """Clear the status text"""
        self.status_text.delete(1.0, "end")
    
    def redirect_stdout(self):
        """Redirect stdout to the status text"""
        self.original_stdout = sys.stdout
        sys.stdout = self.redirector
        return self.original_stdout
    
    def restore_stdout(self, original_stdout):
        """Restore the original stdout"""
        if original_stdout:
            sys.stdout = original_stdout


class SolverGUI:
    """Main GUI class for the CVRP solver"""
    def __init__(self, root):
        self.root = root
        self.root.title("Fashion Reverse Logistics Solver")
        self.root.geometry("700x550")
        
        # Model reference for stopping
        self.current_model = None
        
        # Create the input frame
        self.input_frame = InputFrame(root)
        
        # Create the solver frame
        self.solver_frame = SolverFrame(root)
        
        # Create samples frame
        self._create_samples_frame()
        
        # Create status frame
        self.status_frame = StatusFrame(root)
        
        # Create button frame
        self._create_button_frame()
    
    def _create_samples_frame(self):
        samples_frame = ttk.Frame(self.root)
        samples_frame.pack(fill="x", padx=10, pady=5)
        
        samples_button = ttk.Button(
            samples_frame, 
            text="Create Sample Instances", 
            command=self._create_samples
        )
        samples_button.pack(side="left", padx=5, pady=5)
    
    def _create_button_frame(self):
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Stop button (initially disabled)
        self.stop_button = ttk.Button(
            button_frame, 
            text="Stop Solver", 
            command=self._stop_solver,
            state="disabled"
        )
        self.stop_button.pack(side="right", padx=5)
        
        # Run button
        self.run_button = ttk.Button(
            button_frame, 
            text="Run Solver", 
            command=self._run_solver
        )
        self.run_button.pack(side="right", padx=5)
    
    def _create_samples(self):
        create_sample_instances()
        messagebox.showinfo("Success", "Sample instances created in 'examples' directory")
    
    def _stop_solver(self):
        """Stop the current solver if running"""
        if self.current_model and self.current_model.is_solving():
            print("Stopping optimization...")
            self.current_model.request_stop()
            self.stop_button.config(state="disabled")
    
    def _run_solver(self):
        # Clear status text
        self.status_frame.clear()
        
        # Redirect stdout
        original_stdout = self.status_frame.redirect_stdout()
        
        try:
            # Get instance data
            instance_data = self.input_frame.get_instance_data()
            
            # Get solver parameters
            params = self.solver_frame.get_parameters()
            
            # Load or generate instance
            if instance_data['type'] == 'random':
                print(f"Generating random instance with {instance_data['n_shops']} shops...")
                instance = create_random_problem_instance(
                    instance_data['n_shops'], 
                    instance_data['capacity'], 
                    instance_data['seed']
                )
            else:
                file_path = instance_data['file_path']
                print(f"Loading instance from {file_path}...")
                instance = load_problem_instance(file_path)
            
            # Create and solve the model asynchronously
            self._solve_model_async(instance, params)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
            self.status_frame.restore_stdout(original_stdout)
    
    def _solve_model_async(self, instance, params):
        """Create and solve the model in a background thread"""
        method = params['method']
        time_limit = params['time_limit']
        
        # Create and configure model
        print(f"Creating {method} model...")
        self.current_model = create_model(method, instance)
        
        # Add additional parameters
        solver_params = {'time_limit': time_limit, 'verbose': True}
        if method == 'heuristic':
            solver_params['iterations'] = params.get('iterations', 100)
            solver_params['random_state'] = 42
        
        # Disable run button and enable stop button
        self.run_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Start solving in background thread
        print(f"\nSolving using {method} approach...")
        start_time = time.time()
        
        def on_solve_complete(solution_obj):
            elapsed_time = time.time() - start_time
            print(f"\nSolution completed in {elapsed_time:.2f} seconds")
            
            # Process solution (no need to pass instance)
            self._process_solution(solution_obj)
            
            # Re-enable run button and disable stop button
            self.root.after(0, lambda: self.run_button.config(state="normal"))
            self.root.after(0, lambda: self.stop_button.config(state="disabled"))
        
        # Start solving asynchronously
        self.current_model.solve_async(callback=on_solve_complete, **solver_params)
    
    def _process_solution(self, solution_obj):
        """Process and display the solution"""
        if self.current_model.is_solved():
            # Display solution information
            self.current_model.print_solution_summary()
            
            # Print solution details
            solution_obj.print_summary()
            
            # Save solution files
            solution_obj.save_solution_files()
            
            # Generate visualization
            output_file = "reverse_logistics_solution.png"
            solution_obj.visualize(output_file)
            
            messagebox.showinfo("Success", f"{self.current_model.name} optimization completed! Results saved.")
        else:
            print("No solution found!")


def run_gui():
    """Run the GUI interface"""
    root = tk.Tk()
    app = SolverGUI(root)
    root.mainloop()