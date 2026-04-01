# Noise and Transfer Function Analysis

This repo contains data and analysis scripts for an experiment at the University of Western Australia demonstrating Johnson Noise. The project focuses on characterizing the transfer function and noise characteristics of an amplifier/circuit using various resistor values.

## Project Overview

The objective of this project is to:
1.  **Fit the Transfer Function**: Determine the frequency response $A(f)$ and $H(f, R, C_0)$ parameters of the measurement system.
2.  **Extract Noise Levels**: Calculate the input-referred noise spectral density ($S_{Total}$) equivalent to the Johnson Noise of the Resistors + Current Noise from a Low-Noise Amplifier. Repeated for various resistor values and compared them with theoretical thermal noise ($4k_BTR$).

## File Structure

### Data Files
- `Data000Freq++.txt`: Frequency response data used to fit the system's gain $A_0$ and corner frequencies $f_1, f_2$.
- `Data001Freq++.txt` to `Data008Freq++.txt`: Frequency response measurements with different resistors (3k$\Omega$ to 10M$\Omega$) for $C_0$ extraction.
- `Data009Freq++.txt` / `Data009Freq++2.txt`: Noise floor measurements (short circuit).
- `Data010Freq++.txt` to `Data017Freq++.txt`: Noise measurements for various resistors.
- `Resistor_Values.txt`: Mapping of run IDs to actual measured resistance values (in Ohms).

### Analysis Scripts
- `fit_transfer_func.py`: Core module for fitting the system transfer function $H(f)$. It uses `scipy.optimize.curve_fit` to extract $A_0, f_1, f_2$, and $C_0$.
- `extract_noise.py`: Script that calculates the input-referred noise by subtracting the noise floor and dividing by the squared transfer function.
- `plot_transfer_function.py`: Visualizes the transfer function fits across multiple runs.
- `plot_capacitance.py`: Analyzes and plots the capacitance-related effects.
- `plot_noise_floor.py`: Visualizes the baseline noise floor of the system.

### Generated Results (Plots)
- `transfer_function_000_to_008.png`: Visualization of the initial transfer function fits.
- `extracted_noise_total.png`: Final plot showing the noise spectral density vs theory.
- `fit_capacitance.png` & `A_Transfer_Function.png`: Detailed fitting results.

## Getting Started

### Prerequisites
Ensure you have the following Python libraries installed:
```bash
pip install numpy pandas matplotlib scipy
```

### Running the Analysis
To extract the noise levels and generate the summary plot:
```bash
python extract_noise.py
```
To view the transfer function fitting parameters:
```bash
python fit_transfer_func.py
```

## Physics Context
The analysis follows the theoretical model:
$$H(f, R, C_0) = \frac{A_0 \cdot \frac{f}{f_1}}{\sqrt{1 + \left(\frac{f}{f_1}\right)^2} \sqrt{1 + \left(\frac{f}{f_2}\right)^2} \sqrt{1 + (2\pi f R C_0)^2}}$$
Input-referred noise is extracted using:
$$S_{Total}(f) = \frac{S_{Out}(f) - S_{Floor}(f)}{|H(f)|^2}$$
Comparison with thermal noise is made using the formula $S_{Th} = 4k_BT R$.
