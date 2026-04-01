import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from fit_transfer_func import transfer_func_A, transfer_func_H
from extract_noise import get_noise_analysis_data

def plot_all_transfer_functions():
    """Plots all raw transfer function magnitude data from Runs 000-008."""
    print("Generating transfer function overview plot (Runs 000-008)...")
    mapping = {
        "Data000Freq++.txt": "Reference (TF Amplitude)",
        "Data001Freq++.txt": "33k \u03a9",
        "Data002Freq++.txt": "3k \u03a9",
        "Data003Freq++.txt": "30k \u03a9",
        "Data004Freq++.txt": "100k \u03a9",
        "Data005Freq++.txt": "300k \u03a9",
        "Data006Freq++.txt": "3M \u03a9",
        "Data007Freq++.txt": "1M \u03a9",
        "Data008Freq++.txt": "10M \u03a9"
    }
    plt.figure(figsize=(12, 8))
    for filename, label in mapping.items():
        if os.path.exists(filename):
            df = pd.read_csv(filename, sep='\s+')
            plt.plot(df.iloc[:, 0], df.iloc[:, 1], label=label, alpha=0.8, linewidth=1)
    
    plt.title('Transfer Function Magnitude vs Frequency (Runs 000-008)', fontsize=14)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.xscale('log')
    plt.yscale('log')
    plt.legend(title='Resistor', loc='best', fontsize='small', ncol=2)
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.tight_layout()
    plt.savefig('transfer_function_000_to_008.png')
    plt.close()

def plot_system_fit(params):
    """Plots the fit for the system transfer function A(f) using Data000."""
    print("Generating system fit plot A(f)...")
    df0 = pd.read_csv("Data000Freq++.txt", sep='\s+')
    f, m = df0.iloc[:, 0].values, df0.iloc[:, 1].values
    mask = f > 0
    
    plt.figure(figsize=(10, 6))
    plt.plot(f[mask], m[mask], 'k.', markersize=2, alpha=0.3, label='Data000')
    f_model = np.logspace(0, 5, 1000)
    plt.plot(f_model, transfer_func_A(f_model, params['A_0'], params['f1'], params['f2']), 'r-', 
             label=f"Fit: A_0={params['A_0']:.1f}, f1={params['f1']:.1f}Hz, f2={params['f2']:.1f}Hz")
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title('System Transfer Function $A(f)$ Fit')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.savefig('A_Transfer_Function.png')
    plt.close()

def plot_noise_floor():
    """Plots the baseline noise floor (Run 009)."""
    print("Generating noise floor plot...")
    noise_file = "Data009Freq++2.txt" if os.path.exists("Data009Freq++2.txt") else "Data009Freq++.txt"
    if os.path.exists(noise_file):
        df = pd.read_csv(noise_file, sep='\s+')
        plt.figure(figsize=(10, 6))
        plt.plot(df.iloc[:, 0], df.iloc[:, 1], color='red', alpha=0.8, label='Noise Floor (Short Circuit)')
        plt.xscale('log')
        plt.yscale('log')
        plt.title('System Noise Floor Magnitude')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')
        plt.grid(True, which="both", ls="-", alpha=0.5)
        plt.legend()
        plt.savefig('noise_floor_009.png')
        plt.close()

def plot_noise_results(noise_data):
    """Plots the extracted input-referred noise S_total from the analysis data."""
    if not noise_data:
        print("No noise data available to plot.")
        return

    print("Generating extracted noise plot (S_total)...")
    plt.figure(figsize=(12, 8))
    for run_id, data in noise_data.items():
        f = data['f']
        s_total = data['s_total']
        s_th = data['s_th']
        r_label = data['R_label']
        
        mask = (f > 20) & (f < 20000)
        line = plt.loglog(f[mask], s_total[mask], alpha=0.5, label=f'Run {run_id} (R={r_label})')
        plt.axhline(y=s_th, color=line[0].get_color(), linestyle='--', alpha=0.3)

    plt.title('Extracted Input-Referred Noise Spectral Density $S_{Total}(f)$', fontsize=14)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('$S_{Total}$ ($V^2/Hz$)')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.legend(ncol=2, fontsize='small')
    plt.tight_layout()
    plt.savefig('extracted_noise_total.png')
    plt.close()

if __name__ == "__main__":
    # Get noise analysis data
    noise_data, params = get_noise_analysis_data()
    
    # Perform plotting
    plot_all_transfer_functions()
    plot_system_fit(params)
    plot_noise_floor()
    plot_noise_results(noise_data)
    
    print("\nAll plots have been generated successfully.")
