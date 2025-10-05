import copy
import numpy as np
from scipy.optimize import differential_evolution
from pyH2A.Discounted_Cash_Flow import Discounted_Cash_Flow, discounted_cash_flow_function
from pyH2A.Utilities.input_modification import convert_input_to_dictionary, parse_parameter, get_by_path

class Optimization_Analysis:
    '''Optimization analysis to minimize levelized cost of hydrogen.

    Parameters
    ----------
    Optimization_Analysis > Method > Value : str, optional
        Optimization method. Default is 'differential_evolution'.
    Optimization_Analysis > Max_Iterations > Value : int, optional
        Maximum number of iterations. Default is 1000.
    Optimization_Analysis > Tolerance > Value : float, optional
        Optimization tolerance. Default is 1e-6.
    Parameters - Optimization_Analysis > [...] > Name : str
        Display name for parameter.
    Parameters - Optimization_Analysis > [...] > Lower_Bound : float
        Lower bound for parameter optimization.
    Parameters - Optimization_Analysis > [...] > Upper_Bound : float
        Upper bound for parameter optimization.

    Notes
    -----
    `Parameters - Optimization_Analysis` contains parameters to be optimized for minimum LCOH₂.
    First column specifies path to parameter in input file 
    (top key > middle key > bottom key format).
    '''

    def __init__(self, input_file):
        self.inp = convert_input_to_dictionary(input_file)
        self.base_case = Discounted_Cash_Flow(input_file, print_info=False)
        self.input_file = input_file
        
        self.parameters = []
        self.bounds = []
        self.parameter_names = []
        
        if 'Parameters - Optimization_Analysis' in self.inp:
            for param_path, param_data in self.inp['Parameters - Optimization_Analysis'].items():
                # Split parameter path into list format for set_by_path
                self.parameters.append(param_path.split(' > '))
                self.parameter_names.append(param_data.get('Name', param_path))
                
                # Parse bounds - they should be direct numeric values, not parameter paths
                try:
                    lower_bound = param_data.get('Lower_Bound')
                    upper_bound = param_data.get('Upper_Bound')
                    
                    # Convert to float if not already numeric
                    lower = float(lower_bound) if not isinstance(lower_bound, (int, float)) else lower_bound
                    upper = float(upper_bound) if not isinstance(upper_bound, (int, float)) else upper_bound
                    
                    # Ensure bounds are valid finite numbers
                    if not (isinstance(lower, (int, float)) and isinstance(upper, (int, float))):
                        raise ValueError(f"Bounds for {param_path} must be numeric")
                    if not (np.isfinite(lower) and np.isfinite(upper)):
                        raise ValueError(f"Bounds for {param_path} must be finite")
                    if lower >= upper:
                        raise ValueError(f"Lower bound must be less than upper bound for {param_path}")
                    
                    self.bounds.append((float(lower), float(upper)))
                except Exception as e:
                    print(f"Error parsing bounds for parameter '{param_path}': {e}")
                    print(f"  Lower_Bound: {param_data.get('Lower_Bound')} (type: {type(param_data.get('Lower_Bound'))})")
                    print(f"  Upper_Bound: {param_data.get('Upper_Bound')} (type: {type(param_data.get('Upper_Bound'))})")
                    raise
        
        # Optimization settings
        opt_config = self.inp.get('Optimization_Analysis', {})
        self.method = opt_config.get('Method', {}).get('Value', 'differential_evolution')
        
        # Parse max_iter and tolerance as numeric values, not parameter paths
        max_iter_value = opt_config.get('Max_Iterations', {}).get('Value', 1000)
        self.max_iter = int(max_iter_value) if not isinstance(max_iter_value, int) else max_iter_value
        
        tolerance_value = opt_config.get('Tolerance', {}).get('Value', 1e-6)
        self.tolerance = float(tolerance_value) if not isinstance(tolerance_value, float) else tolerance_value
        
        # Store baseline LCOH₂
        self.baseline_lcoh2 = self.base_case.h2_cost
        
        # Perform optimization
        self.results = self.optimize()
        self.print_results()

    def objective_function(self, x):
        '''Objective function to minimize LCOH₂.'''
        try:
            # Wrap x in a list to match expected format for discounted_cash_flow_function
            # which expects an iterable of value sets
            results = discounted_cash_flow_function(
                self.inp, [x], self.parameters, attribute='h2_cost'
            )
            # Return the first (and only) result
            lcoh = results[0]
            # Debug: print first few evaluations
            if not hasattr(self, '_eval_count'):
                self._eval_count = 0
            self._eval_count += 1
            if self._eval_count <= 5:
                print(f"Evaluation {self._eval_count}: x={x}, LCOH₂=${lcoh:.4f}/kg")
            return lcoh
        except Exception as e:
            print(f"Error in objective function: {e}")
            print(f"Parameters: {x}")
            import traceback
            traceback.print_exc()
            return 1e6

    def optimize(self):
        '''Perform optimization to minimize LCOH₂.'''
        if not self.parameters:
            return {'success': False, 'message': 'No parameters specified'}
        
        result = differential_evolution(
            self.objective_function,
            self.bounds,
            maxiter=self.max_iter,
            tol=self.tolerance,
            seed=42
        )
        
        return {
            'success': result.success,
            'optimal_lcoh2': result.fun,
            'baseline_lcoh2': self.baseline_lcoh2,
            'optimal_values': result.x,
            'baseline_values': [get_by_path(self.inp, p) for p in self.parameters]
        }

    def print_results(self):
        '''Print optimization results.'''
        if not self.results['success']:
            print(f"Optimization failed")
            return
        
        print("=== Optimization Results ===")
        print(f"Baseline LCOH₂: ${self.results['baseline_lcoh2']:.4f}/kg")
        print(f"Optimal LCOH₂:  ${self.results['optimal_lcoh2']:.4f}/kg")
        reduction = self.results['baseline_lcoh2'] - self.results['optimal_lcoh2']
        reduction_pct = (reduction / self.results['baseline_lcoh2']) * 100
        print(f"Reduction:      ${reduction:.4f}/kg ({reduction_pct:.2f}%)")
        print()
        
        print("Optimized Parameter Values:")
        for i, name in enumerate(self.parameter_names):
            baseline = self.results['baseline_values'][i]
            optimal = self.results['optimal_values'][i]
            print(f"  {name}: {optimal:.2f} (baseline: {baseline:.2f})")


