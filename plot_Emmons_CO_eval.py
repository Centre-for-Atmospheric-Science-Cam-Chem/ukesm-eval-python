import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

class CO_Evaluation:
    def __init__(self, model_path, obs_dir, out_dir, mod_name):
        self.model_path = Path(model_path)
        self.obs_dir = Path(obs_dir)
        self.out_dir = Path(out_dir)
        self.mod_name = mod_name
        self.conv = 1e9  # Conversion factor for units (ppb or ppt)
        self.mm_co = 28.01  # Molar mass of CO
        
        # Create output directory if it doesn't exist
        self.out_dir.mkdir(parents=True, exist_ok=True)
        
    def load_model_data(self, dataset_name, co_code, lon1, lat1, d_lon, d_lat, hgt):
        """Load model data from NetCDF file"""
        with xr.open_dataset(self.model_path) as ds:
            model_data = ds[co_code].sel(
                longitude=slice(lon1, lon1 + d_lon),
                latitude=slice(lat1, lat1 + d_lat)
            ).values * (self.conv / self.mm_co)
            
        # Calculate quantiles
        model_stats = np.quantile(model_data, [0.25, 0.5, 0.75], axis=(0, 1, 3))
        return model_stats
    
    def load_obs_data(self, obs_file):
        """Load observation data from file"""
        if obs_file.suffix == '.csv':
            obs_data = pd.read_csv(obs_file, header=None, skiprows=1)
        else:
            obs_data = pd.read_csv(obs_file, delim_whitespace=True, header=None)
        
        # Calculate standard deviation bounds
        obs_data['sd_upper'] = obs_data[4] + obs_data[5]
        obs_data['sd_lower'] = obs_data[4] - obs_data[5]
        return obs_data
    
    def create_comparison_plot(self, model_stats, obs_data, site_info, hgt_levels=10):
        """Create a single comparison plot"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot observations with uncertainty
        ax.errorbar(obs_data[4], obs_data[0], 
                   xerr=obs_data[5], fmt='o', 
                   color='black', label='Observations')
        ax.fill_betweenx(obs_data[0], obs_data['sd_lower'], obs_data['sd_upper'],
                        color='gray', alpha=0.3)
        
        # Plot model with interquartile range
        ax.plot(model_stats[1][:hgt_levels], obs_data[0][:hgt_levels], 
               'r-', label=self.mod_name)
        ax.fill_betweenx(obs_data[0][:hgt_levels], 
                         model_stats[0][:hgt_levels], 
                         model_stats[2][:hgt_levels],
                         color='red', alpha=0.3)
        
        # Customise plot
        ax.set_xlabel('CO (ppbv)')
        ax.set_ylabel('Altitude (km)')
        ax.set_title(
            f"{site_info['name']} {site_info['date'].strftime('%Y %m')}\n"
            f"Lat {site_info['lat_min']}-{site_info['lat_max']} "
            f"Lon {site_info['lon_min']}-{site_info['lon_max']}"
        )
        ax.grid(True)
        ax.legend()
        
        return fig
    
    def run_all_comparisons(self, sites_config):
        """Run comparisons for all configured sites"""
        plt.figure(figsize=(16, 24))
        
        for i, (site_name, config) in enumerate(sites_config.items(), 1):
            # Load data
            model_stats = self.load_model_data(
                site_name, config['co_code'], 
                config['lon1'], config['lat1'],
                config['d_lon'], config['d_lat'],
                config['hgt']
            )
            
            obs_data = self.load_obs_data(
                self.obs_dir / config['obs_path']
            )
            
            # Create plot
            plt.subplot(4, 3, i)
            self.create_comparison_plot(
                model_stats, obs_data, config['site_info']
            )
        
        # Save final output
        plt.tight_layout()
        plt.savefig(self.out_dir / f"{self.mod_name}_Emmons_CO_Multi.png")
        plt.close()

# Example configuration (would need to be filled with actual values)
sites_config = {
    'intex.na.ec': {
        'co_code': 'co_var_name',
        'lon1': -125.0,
        'lat1': 45.0,
        'd_lon': 10.0,
        'd_lat': 10.0,
        'hgt': 10,
        'obs_path': 'INTEX-NA/INTEX-NA_EC_co.stat',
        'site_info': {
            'name': 'INTEX-NA EC',
            'date': pd.to_datetime('2006-07-01'),
            'lat_min': 40.0,
            'lat_max': 50.0,
            'lon_min': -130.0,
            'lon_max': -120.0
        }
    },
    # Add configurations for other sites similarly
}

# Initialise and run the evaluation
evaluator = CO_Evaluation(
    model_path='path/to/model_output.nc',
    obs_dir='path/to/obs_data',
    out_dir='output',
    mod_name='xgywn'
)

evaluator.run_all_comparisons(sites_config)