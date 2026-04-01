import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import os

# Configuration
DATA_DIR = "data"

# Formula: A(f) = A_0 * (f/f1) / (sqrt(1+(f/f1)^2) * sqrt(1+(f/f2)^2))
def transfer_func_A(f, A_0, f1, f2):
    f = np.array(f, dtype=float)
    f[f == 0] = 1e-9 # avoid div 0
    return A_0 * (f/f1) / (np.sqrt(1 + (f/f1)**2) * np.sqrt(1 + (f/f2)**2))

# Formula: H(f, R, C_0) = A(f) / sqrt(1+(2*pi*f*R*C_0)^2)
def transfer_func_H(f, R, C_0, A_0, f1, f2):
    return transfer_func_A(f, A_0, f1, f2) / np.sqrt(1 + (2 * np.pi * f * R * C_0)**2)

def get_fit_params():
    # Load Measured Resistor Values
    resistor_path = os.path.join(DATA_DIR, "Resistor_Values.txt")
    resistor_df = pd.read_csv(resistor_path, sep='\s+', comment='#', names=['Run_ID', 'R_val'])
    resistor_actuals = dict(zip(resistor_df['Run_ID'].astype(int), resistor_df['R_val']))

    # Fit for A(f) system parameters using Data000 
    data0_path = os.path.join(DATA_DIR, "Data000Freq++.txt")
    df0 = pd.read_csv(data0_path, sep='\s+')
    freq0 = df0.iloc[:, 0].values
    mag0 = df0.iloc[:, 1].values
    mask0 = freq0 > 0
    freq0_fit, mag0_fit = freq0[mask0], mag0[mask0]

    p0_A = [np.max(mag0_fit), 12, 16000]
    popt0, pcov0 = curve_fit(transfer_func_A, freq0_fit, mag0_fit, p0=p0_A)
    A_0_sys, f1_sys, f2_sys = popt0
    
    # Fit for C_0 using Data001 to Data008
    all_freqs, all_mags, all_Rs = [], [], []
    for run_id in range(1, 9):
        if run_id in resistor_actuals:
            R_val = resistor_actuals[run_id]
            try:
                data_path = os.path.join(DATA_DIR, f"Data{run_id:03d}Freq++.txt")
                df = pd.read_csv(data_path, sep='\s+')
                f, m = df.iloc[:, 0].values, df.iloc[:, 1].values
                mask = f > 0
                all_freqs.extend(f[mask]); all_mags.extend(m[mask]); all_Rs.extend([R_val] * np.sum(mask))
            except Exception: pass

    def joint_fit(f_R_tuple, C_0):
        f, R = f_R_tuple
        return transfer_func_H(f, R, C_0, A_0_sys, f1_sys, f2_sys)

    popt_C = curve_fit(joint_fit, (np.array(all_freqs), np.array(all_Rs)), np.array(all_mags), p0=[10e-12])
    C_0_fit = popt_C[0]
    
    return {
        'A_0': A_0_sys,
        'f1': f1_sys,
        'f2': f2_sys,
        'C_0': C_0_fit,
        'resistor_actuals': resistor_actuals
    }

if __name__ == "__main__":
    params = get_fit_params()
    print(f"A_0: {params['A_0']:.4f}")
    print(f"f1_sys: {params['f1']:.4f} Hz")
    print(f"f2_sys: {params['f2']:.4f} Hz")
    print(f"Extracted C_0: {params['C_0']*1e12:.2f} pF")
