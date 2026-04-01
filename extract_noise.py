import numpy as np
import pandas as pd
import os
from fit_transfer_func import get_fit_params, transfer_func_H

# Configuration
DATA_DIR = "data"

# Constants
k_B = 1.380649e-23
T = 295  # Room temp approx 22C

def extract_s_total(run_id, R_val, params, f_floor, s_out_floor):
    """Extracts S_total for a single run ID."""
    try:
        filename = os.path.join(DATA_DIR, f"Data{run_id:03d}Freq++.txt")
        if not os.path.exists(filename):
            return None, None
            
        df = pd.read_csv(filename, sep='\s+')
        f, s_out = df.iloc[:, 0].values, df.iloc[:, 1].values**2
        
        # S_total = (S_out - S_out_floor) / |H(f)|^2
        s_diff = s_out - s_out_floor
        h_f = transfer_func_H(f, R_val, params['C_0'], params['A_0'], params['f1'], params['f2'])
        s_total = s_diff / (h_f**2)
        
        return f, s_total
    except Exception as e:
        print(f"Error processing Run {run_id}: {e}")
        return None, None

def get_noise_analysis_data():
    """
    Performs noise extraction, prints the summary table, 
    and returns the raw data for plotting.
    """
    print("Fetching fit parameters...")
    params = get_fit_params()
    resistor_actuals = params['resistor_actuals']

    # Load Noise Floor
    noise_floor_file2 = os.path.join(DATA_DIR, "Data009Freq++2.txt")
    noise_floor_file1 = os.path.join(DATA_DIR, "Data009Freq++.txt")
    noise_floor_file = noise_floor_file2 if os.path.exists(noise_floor_file2) else noise_floor_file1
    
    if not os.path.exists(noise_floor_file):
        print(f"Error: Noise floor file not found.")
        return None, params

    floor_df = pd.read_csv(noise_floor_file, sep='\s+')
    f_floor = floor_df.iloc[:, 0].values
    s_out_floor = floor_df.iloc[:, 1].values**2

    plot_data = {}
    summary_data = []

    print("\nProcessing runs and extracting noise levels...")
    for run_id in range(10, 18):
        if run_id in resistor_actuals:
            R_val = resistor_actuals[run_id]
            f, s_total = extract_s_total(run_id, R_val, params, f_floor, s_out_floor)
            
            if f is not None:
                s_th = 4 * k_B * T * R_val
                
                # Store for plotting
                plot_data[run_id] = {
                    'f': f,
                    's_total': s_total,
                    's_th': s_th,
                    'R_label': f'{R_val/1e3:.1f}k\u03a9'
                }
                
                # Summary Calculation (Average between 200Hz and 2kHz)
                mask_flat = (f > 200) & (f < 2000)
                avg_s = np.median(s_total[mask_flat])
                summary_data.append((run_id, R_val/1e3, avg_s, s_th))

    # Print Summary Table
    print(f"\n{'Run':<5} {'R (kOhm)':<10} {'S_total (avg)':<15} {'4kTR (theory)':<15}")
    for run_id, r_k, avg_s, s_th in summary_data:
        print(f"{run_id:<5} {r_k:<10.2f} {avg_s:<15.2e} {s_th:<15.2e}")
        
    return plot_data, params

if __name__ == "__main__":
    # Run directly to perform analysis and print the table
    get_noise_analysis_data()
