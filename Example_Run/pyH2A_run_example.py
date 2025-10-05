import os
from pathlib import Path
from pyH2A.run_pyH2A import pyH2A

def run_pyH2A_example():
    # Get the project root directory (parent of Example_Run)
    project_root = Path(__file__).parent.parent
    
    # Use absolute paths
    input_file = project_root / 'data' / 'PV_E' / 'Base' / 'PV_E_Base.md'
    output_dir = project_root / 'data' / 'PV_E' / 'Base'
    
    # Change to project root so relative paths in the input file work correctly
    os.chdir(project_root)
    
    result = pyH2A(str(input_file), str(output_dir))
    return result

if __name__ == '__main__':
    run_pyH2A_example()
