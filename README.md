# Johnson Noise: Noise and Transfer Function Analysis

This repository contains data and scripts for an experiment conducted at the University of Western Australia to characterize **Johnson-Nyquist noise**.

## Project Overview

The objective of this project is to:
1.  **Fit the System Transfer Function**: Determine the frequency response $A(f)$ and $H(f, R, C_0)$ parameters of the system.
2.  **Extract Noise Levels**: Calculate the input-referred noise spectral density ($S_{Total}$) equivalent to the Johnson Noise of the Resistors plus the Current Noise from a Low-Noise Amplifier. 

## File Structure

### Project Root
- `generate_plots.py`: Unified script to perform analysis and generate all project plots. Run this script only to reproduce full analysis, using below scripts as modules.
- `extract_noise.py`: Module for extracting noise spectral density and calculating summary statistics.
- `fit_transfer_func.py`: Module for fitting the system transfer function $H(f, R)$.

### Data Directory (`data/`)
- `Data000Freq++.txt` to `Data029Freq++.txt`: Raw measurement data.
- `Resistor_Values.txt`: Measured resistance values for each run.
- `Temperature_Values.txt`: Measured temperature values for each run.

### Images Directory (`images/`)
The following images are generated from the generate_plots.py script. Images 2-4 & 6 were used for the report.
1.  **`A_Transfer_Function.png`**: Plot of the system transfer function $A(f)$
2.  **`boltzmann_fit_regression.png`**: Linear regression of $S_{total}/R^2$ vs. $T/R$ used to extract the Boltzmann constant ($k_B$)
3.  **`extracted_noise_room_temp.png`**: Extracted input-referred noise power spectral density $S_{Total}(f)$ for room temperature measurements (Runs 10-17)
4.  **`extracted_noise_temp_dep.png`**: Extracted input-referred noise power spectral density $S_{Total}(f)$ for temperature-dependent measurements (Runs 18-29)
5.  **`noise_floor_009.png`**: Baseline system noise floor magnitude (Run 009) captured with a short-circuit input to characterize instrument noise.
6.  **`transfer_function_000_to_008.png`**: Comprehensive overview of transfer function magnitudes for various resistor loads (Runs 000-008)

## Running the Code

### Prerequisites
Ensure you have the following Python libraries installed in your environment:
```bash
pip install numpy pandas matplotlib scipy
```

### Running the Analysis
To perform the full analysis and regenerate all plots:
```bash
python generate_plots.py
```
