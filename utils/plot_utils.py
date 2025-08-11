import matplotlib.pyplot as plt

def set_plot_style():
    plt.rcParams.update({
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "legend.fontsize": 10,
        "axes.grid": True,
    })

def plot_station_seasonal(ax, obs_mean, obs_std, mod_mean, site, lat, lon, r, mbe, ylim, plot_units):
    ew = "W" if lon < 0 else "E"
    ns = "S" if lat < 0 else "N"
    ax.errorbar(range(1, 13), obs_mean, yerr=obs_std, fmt="-ok", mfc="white", capsize=3, label="obs")
    ax.plot(range(1, 13), mod_mean, "-or", mfc="white", label="model")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    ax.set_title(f"{site} ({abs(lat):.1f}°{ns}, {abs(lon):.1f}°{ew})", fontsize=10, weight="bold")
    ax.set_xticks([1, 3, 5, 7, 9, 11])
    ax.set_xticklabels(["Jan", "Mar", "May", "Jul", "Sep", "Nov"])
    ax.set_ylabel(f"CO ({plot_units})")
    if ylim is not None:
        ax.set_ylim(ylim)
    ax.text(0.5, 0.05, f"r = {r:.3f}   MBE = {mbe:.1f}%", transform=ax.transAxes, ha="center", fontsize=9)
