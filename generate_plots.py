import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from fit_transfer_func import transfer_func_A, transfer_func_H
from extract_noise import get_noise_analysis_data, k_B, T_ROOM

# Configuration
DATA_DIR = "data"
IMAGE_DIR = "images"

# Ensure image directory exists
os.makedirs(IMAGE_DIR, exist_ok=True)

def plot_boltzmann_fit(noise_data, params):
    """
    Plots the linear regression: S_total/R^2 = S_i + 4*k_B*(T/R).
    Fits for S_i (current noise) and k_B (Boltzmann constant).
    """
    print("Generating Boltzmann fit and linear regression plot...")
    from scipy.optimize import curve_fit

    data_points = []
    for run_id, data in noise_data.items():
        if run_id in params['resistor_actuals']:
            R_val = params['resistor_actuals'][run_id]
            f, s_total, t_val = data['f'], data['s_total'], data['T']

            # Average S_total in the flat region (200Hz - 2kHz)
            mask_flat = (f > 200) & (f < 2000)
            s_avg = np.median(s_total[mask_flat])

            # Relation: S_total/R^2 = S_i + 4*k_B*(T/R)
            data_points.append((run_id, t_val / R_val, s_avg / (R_val**2)))

    # Sort for plotting and mapping
    data_points.sort(key=lambda p: p[1])
    run_ids = [p[0] for p in data_points]
    xs = np.array([p[1] for p in data_points])
    ys = np.array([p[2] for p in data_points])

    # Linear model: y = S_i + (4*k_B) * x
    def model(x, S_i, four_kB):
        return S_i + four_kB * x

    popt, _ = curve_fit(model, xs, ys)
    S_i_fit, four_kB_fit = popt
    kB_fit = four_kB_fit / 4

    # Plotting with Residuals
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)

    # Main fit plot
    ax1.plot(xs, ys, 'bo', label='Data (Runs 10-29)')
    
    x_line = np.linspace(0, max(xs)*1.1, 100)
    ax1.plot(x_line, model(x_line, *popt), 'r-', 
             label=f'Fit: $k_B$={kB_fit:.2e} J/K\n$S_i$={S_i_fit:.2e} $A^2/Hz$')

    ax1.set_ylabel('$S_{total} / R^2$ ($A^2/Hz$)', labelpad=15)
    ax1.set_title('Linear Regression: Noise Analysis for Boltzmann Constant', fontsize=14)
    ax1.legend()
    ax1.grid(True, which="both", ls="-", alpha=0.5)

    # Residuals plot
    residuals = ys - model(xs, *popt)
    ax2.plot(xs, residuals, 'ro')
    ax2.axhline(0, color='black', linestyle='--')
    ax2.set_xlabel('$T / R$ ($K/\Omega$)')
    ax2.set_ylabel('Residuals ($A^2/Hz$)', labelpad=15)
    ax2.grid(True, which="both", ls="-", alpha=0.5)

    plt.tight_layout(rect=[0.03, 0.03, 1, 0.95])
    plt.savefig(os.path.join(IMAGE_DIR, 'boltzmann_fit_regression.png'))
    plt.close()

    print(f"Regression Results:")
    print(f"  Extracted k_B: {kB_fit:.4e} J/K (Expected: 1.38e-23)")
    print(f"  Extracted S_i: {S_i_fit:.4e} A^2/Hz")

def plot_all_transfer_functions(params):
    """Plots all raw transfer function magnitude data from Runs 000-008, including the global fits."""
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
    f_model = np.logspace(0, 5, 500)
    for filename, label in mapping.items():
        data_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(data_path):
            df = pd.read_csv(data_path, sep='\s+')
            line = plt.plot(df.iloc[:, 0], df.iloc[:, 1], label=label, alpha=0.4, linewidth=1)  
            color = line[0].get_color()
            try: 
                run_id = int(filename[4:7])  
                if run_id == 0:   
                    y_model = transfer_func_A(f_model, params['A_0'], params['f1'], params['f2']) 
                elif run_id in params['resistor_actuals']: 
                    R_val = params['resistor_actuals'][run_id]
                    y_model = transfer_func_H(f_model, R_val, params['C_0'], params['A_0'], params['f1'], params['f2'])
                else:
                    continue
                plt.plot(f_model, y_model, color=color, linestyle='--', alpha=0.8, linewidth=1.5)
            except Exception:
                pass
    plt.plot([],[],'k--', alpha=0.8, label='Theoretical Fit')
    plt.title('Transfer Function Magnitude vs Frequency (Runs 000-008)', fontsize=14)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.xscale('log')
    plt.yscale('log')
    plt.legend(title='Resistor / Fit', loc='best', fontsize='small', ncol=2)
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGE_DIR, 'transfer_function_000_to_008.png'))
    plt.close()

def plot_system_fit(params):
    """Plots the fit for the system transfer function A(f) using Data000."""
    print("Generating system fit plot A(f)...")
    data0_path = os.path.join(DATA_DIR, "Data000Freq++.txt")
    df0 = pd.read_csv(data0_path, sep='\s+')
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
    plt.savefig(os.path.join(IMAGE_DIR, 'A_Transfer_Function.png'))
    plt.close()

def plot_noise_floor():
    """Plots the baseline noise floor (Run 009)."""
    print("Generating noise floor plot...")
    noise_file2 = os.path.join(DATA_DIR, "Data009Freq++2.txt")
    noise_file1 = os.path.join(DATA_DIR, "Data009Freq++.txt")
    noise_file = noise_file2 if os.path.exists(noise_file2) else noise_file1
    
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
        plt.savefig(os.path.join(IMAGE_DIR, 'noise_floor_009.png'))
        plt.close()

def plot_noise_results(noise_data):
    """Plots the extracted input-referred noise S_total in two separate plots."""
    if not noise_data:
        print("No noise data available to plot.")
        return

    # Plot 1: Room Temperature Runs (10-17)
    print("Generating room temperature noise plot (Runs 10-17)...")
    plt.figure(figsize=(12, 8))
    for run_id in range(10, 18):
        if run_id in noise_data:
            data = noise_data[run_id]
            f, s_total, s_th, r_label = data['f'], data['s_total'], data['s_th'], data['R_label']
            mask = (f > 20) & (f < 20000)
            line = plt.loglog(f[mask], s_total[mask], alpha=0.5, label=f'Run {run_id} ({r_label})')
            plt.axhline(y=s_th, color=line[0].get_color(), linestyle='--', alpha=0.3)

    plt.title('Extracted Input-Referred Noise $S_{Total}(f)$ - Room Temp Runs (10-17)', fontsize=14)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('$S_{Total}$ ($V^2/Hz$)')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.legend(ncol=2, fontsize='small')
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGE_DIR, 'extracted_noise_room_temp.png'))
    plt.close()

    # Plot 2: Temperature Dependent Runs (18-29)
    print("Generating temperature dependent noise plot (Runs 18-29)...")
    plt.figure(figsize=(12, 8))
    for run_id in range(18, 30):
        if run_id in noise_data:
            data = noise_data[run_id]
            f, s_total, s_th, r_label = data['f'], data['s_total'], data['s_th'], data['R_label']
            mask = (f > 20) & (f < 20000)
            line = plt.loglog(f[mask], s_total[mask], alpha=0.5, label=f'Run {run_id} ({r_label})')
            plt.axhline(y=s_th, color=line[0].get_color(), linestyle='--', alpha=0.3)

    plt.title('Extracted Input-Referred Noise $S_{Total}(f)$ - Temp Dependent Runs (18-29)', fontsize=14)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('$S_{Total}$ ($V^2/Hz$)')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.legend(ncol=2, fontsize='small')
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGE_DIR, 'extracted_noise_temp_dep.png'))
    plt.close()

if __name__ == "__main__":
    # Get noise analysis data (this prints the summary table)
    noise_data, params = get_noise_analysis_data()
    
    # Perform plotting
    plot_all_transfer_functions(params)
    plot_system_fit(params)
    plot_noise_floor()
    plot_noise_results(noise_data)
    plot_boltzmann_fit(noise_data, params)
    
    print(f"\nAll plots have been generated successfully in the '{IMAGE_DIR}' folder.")
