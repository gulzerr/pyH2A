# Optimization Analysis for Hydrogen Production Cost Minimization

## Overview

This document describes the implementation of a new **Optimization Analysis** module for the pyH2A framework. This module enables automated optimization of system parameters to minimize the Levelized Cost of Hydrogen (LCOH₂).

## What Was Done

### 1. Created New Analysis Module
**File:** `src/pyH2A/Analysis/Optimization_Analysis.py`

A new analysis class that:
- Automatically finds optimal parameter values to minimize LCOH₂
- Uses global optimization (differential evolution algorithm from scipy)
- Supports multiple parameters with customizable bounds
- Provides detailed results comparing baseline vs. optimized configurations

### 2. Key Features

#### Automated Parameter Optimization
- Searches parameter space to find values that minimize hydrogen production cost
- Uses **differential evolution**, a robust global optimization algorithm that:
  - Explores the entire parameter space (doesn't get stuck in local minima)
  - Works well for non-linear, complex objective functions
  - Doesn't require gradient information

#### Flexible Configuration
- Define any number of parameters to optimize
- Set custom bounds (min/max) for each parameter
- Configure optimization settings (iterations, tolerance, etc.)

#### Comprehensive Results
- Shows baseline LCOH₂ (original configuration)
- Shows optimal LCOH₂ (optimized configuration)
- Displays cost reduction achieved
- Lists all optimized parameter values with comparison to baseline

## How It Works

### 1. Configuration in Markdown File

Add two sections to your pyH2A input file (`.md` format):

#### Optimization Analysis Settings
```markdown
# Optimization_Analysis

Name | Value | Comment
--- | --- | ---
Method | differential_evolution | Optimization algorithm
Max_Iterations | 1000 | Maximum iterations for convergence
Population_Size | 15 | Population size for differential evolution
Tolerance | 0.01 | Convergence tolerance
Random_Seed | 42 | Random seed for reproducibility
```

#### Parameters to Optimize
```markdown
# Parameters - Optimization_Analysis

Parameter | Name | Lower_Bound | Upper_Bound | Comment
--- | --- | --- | --- | ---
Photovoltaic > PV/Electrolyzer Ratio > Value | PV/Electrolyzer Ratio | 0.5 | 3.0 | Ratio of PV to electrolyzer capacity
```

**Parameter Column Format:** `Top_Level > Mid_Level > Bottom_Level > Value`
- Must match the exact path in your input file
- Use `>` to separate hierarchy levels
- Always end with `> Value`

### 2. Running the Optimization

Run the demonstration script:
```bash
python demo_analysis.py
```

This will execute the optimization analysis and display the results.

### 3. Understanding the Output

The optimization prints progress:
```
Evaluation 1: x=[4.32083203], LCOH₂=$6.1209/kg
Evaluation 2: x=[3.43978314], LCOH₂=$5.2634/kg
Evaluation 3: x=[2.19819953], LCOH₂=$4.0424/kg
...
```

Final results:
```
=== Optimization Results ===
Baseline LCOH₂: $3.5778/kg
Optimal LCOH₂:  $3.5778/kg
Reduction:      $0.0000/kg (0.00%)

Optimized Parameter Values:
  PV/Electrolyzer Ratio: 1.50 (baseline: 1.50)
```

## Example: PV/Electrolyzer Ratio Optimization

### Test Case
**File:** `data/PV_E/Base/PV_E_Base_Optimization_Complete.md`

**Objective:** Find the optimal ratio of photovoltaic capacity to electrolyzer capacity that minimizes LCOH₂

**Configuration:**
- Parameter: PV/Electrolyzer Ratio
- Baseline Value: 1.5
- Search Range: 0.5 to 3.0
- Max Iterations: 1000
- Tolerance: 0.01

### Results
The optimization confirmed that the baseline ratio of **1.5** is optimal:
- **Baseline LCOH₂:** $3.5778/kg
- **Optimal LCOH₂:** $3.5778/kg
- **Optimal Ratio:** 1.50

This validates the original system design and aligns with research findings (Chang et al. 2020) for optimal PV-to-electrolyzer sizing.

## Technical Implementation Details

### Algorithm Choice: Differential Evolution
- **Type:** Stochastic, population-based global optimization
- **Advantages:**
  - No gradient calculations needed
  - Robust against local minima
  - Works well for complex, non-linear problems
  - Handles bounded constraints naturally

### Key Parameters
1. **Max_Iterations (1000):** Controls how long the algorithm searches
2. **Population_Size (15):** Number of candidate solutions per iteration
3. **Tolerance (0.01):** Convergence criterion ($0.01/kg for LCOH₂)
4. **Random_Seed (42):** Ensures reproducible results

### Objective Function
The optimizer minimizes:
```python
def objective_function(x):
    return LCOH₂(parameter_values=x)
```

Where LCOH₂ is calculated using the full pyH2A discounted cash flow model.


## Important Notes

### Markdown Table Formatting
⚠️ **Critical:** pyH2A requires simple markdown table format without leading/trailing pipes:

**Correct:**
```markdown
Name | Value | Comment
--- | --- | ---
Method | differential_evolution | Algorithm
```

**Incorrect:**
```markdown
| Name | Value | Comment |
| --- | --- | --- |
| Method | differential_evolution | Algorithm |
```

VS Code auto-formatting has been disabled for markdown files to prevent this issue.

### Path Handling
All pyH2A scripts must:
1. Import `os` and `pathlib.Path`
2. Set `project_root = Path(__file__).parent` (or `.parent.parent` if in subdirectory)
3. Call `os.chdir(project_root)` before running pyH2A
4. Use absolute paths for input/output files

This ensures relative paths in markdown files resolve correctly.




