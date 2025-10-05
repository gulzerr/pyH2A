"""
Demo script to run pyH2A optimization analysis and access results programmatically.
"""

import os
from pathlib import Path
from pyH2A.run_pyH2A import pyH2A


def main():
    """Main function to run the pyH2A analysis."""
    # Get the project root directory
    project_root = Path(__file__).parent
    
    input_file = 'data/PV_E/Base/PV_E_Base_Optimization_Complete.md'
    output_dir = project_root / 'Example_Output'
    
    # Create the output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Change to project root so relative paths in the input file work correctly
    os.chdir(project_root)

    # Run the analysis (results printed to console automatically)
    analysis = pyH2A(str(input_file), str(output_dir))

    # Access optimization results programmatically
    meta_modules = getattr(analysis, 'meta_modules', {})
    if 'Optimization_Analysis' in meta_modules:
        opt_module = meta_modules['Optimization_Analysis']['Module']
        optimization_results = opt_module.results
        print("\n--- Programmatic Access to Results ---")
        print(f"Optimal LCOH₂: ${optimization_results['optimal_lcoh2']:.4f}/kg")
        # The 'optimal_values' are in the same order as the parameters in the input file
        optimized_params = opt_module.parameter_names
        for name, value in zip(optimized_params, optimization_results['optimal_values']):
            print(f"Optimal {name}: {value:.2f}")


if __name__ == '__main__':
    main()