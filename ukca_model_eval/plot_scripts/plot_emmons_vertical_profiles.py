import matplotlib.pyplot as plt
import numpy as np
from utils.data_io import read_emmons_stat_file, match_stat_files_by_basename

def plot_vertical_profiles(model_files, obs_files, out_pdf, nrows=3, ncols=3, species_label="H2O2 (pptv)"):
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols*4, nrows*5), sharey=True)
    axes = axes.flatten()
    npan = min(len(model_files), len(obs_files), nrows*ncols)
    
    for idx in range(npan):
        model_file = model_files[idx]
        obs_file = obs_files[idx]
        model = read_emmons_stat_file(model_file)
        obs = read_emmons_stat_file(obs_file)

        ax = axes[idx]
        # Plot model: mean ± stddev as shaded, mean as line
        ax.plot(model['mean'], model['alt'], 'r-', lw=2, label='xgywn')
        ax.fill_betweenx(model['alt'], model['mean']-model['stddev'], model['mean']+model['stddev'],
                         color='red', alpha=0.25)
        # Plot obs: median as line, 25–75th percentile as shaded
        ax.plot(obs['median'], obs['alt'], 'k-', lw=2, label='Obs')
        ax.fill_betweenx(obs['alt'], obs['p25'], obs['p75'], color='grey', alpha=0.3)
        ax.set_xlabel(species_label)
        ax.set_ylabel('Altitude (km)')
        ax.set_title(model.get('title', ''), fontsize=10)
        ax.invert_yaxis()
        ax.grid(True)
        if idx == 0:
            ax.legend()
    # Hide extra axes if any
    for ax in axes[npan:]:
        ax.axis('off')
    plt.tight_layout()
    plt.savefig(out_pdf)
    print(f"Saved: {out_pdf}")

if __name__ == "__main__":
    # Edit these as needed:
    model_dir = "../data/emmons_model_stats/h2o2/"
    obs_dir = "../data/emmons_obs_stats/h2o2/"
    out_pdf = "../output/h2o2_emmons_vertical_profiles.pdf"
    species_label = "H2O2 (pptv)"
    suffix_model = "_model.txt"
    suffix_obs = "_obs.txt"

    # Use the file-matching utility in utils/data_io.py
    model_files, obs_files = match_stat_files_by_basename(model_dir, obs_dir, suffix_model, suffix_obs)
    plot_vertical_profiles(model_files, obs_files, out_pdf, nrows=3, ncols=3, species_label=species_label)
