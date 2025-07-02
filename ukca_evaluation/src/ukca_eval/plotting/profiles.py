import matplotlib.pyplot as plt

def plot_vertical_stub(model, obs, title="Vertical Profile Stub"):
    """Stub plot: overlay model & obs dummy profiles."""
    fig, ax = plt.subplots()
    ax.plot(model["values"], model["pressure"], label="Model (stub)")
    ax.plot(obs["values"],   obs["pressure"],   label="Obs (stub)", linestyle="--")
    ax.set_ylabel("Pressure (hPa)")
    ax.set_xlabel("Normalized Value")
    ax.set_title(title)
    ax.invert_yaxis()
    ax.legend()
    return fig
