import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import cartopy.crs as ccrs
from busecke_etal_2021_aguadv.utils import o2_models
from xarrayutils.plotting import map_util_plot

def jitter_plot(
    pos,
    datasets,
    model_jitter_amount=0.1,
    model_margin=0.1,
    ax=None,
    alpha=1.0,
    bars=True,
    s=25,
    **kwargs
):

    kwargs.setdefault("s", 35)

    if ax is None:
        ax = plt.gca()

    model_margin = model_margin * model_jitter_amount

    # first determine the model cluster positions
    n_models = len(datasets)
    pos_model = np.random.choice(
        np.linspace(pos - model_jitter_amount, pos + model_jitter_amount, n_models),
        size=n_models,
        replace=False,
    )
    member_jitter_amount = (model_jitter_amount - model_margin) / n_models

    model_member_averaged = []

    for model, p_model in zip(datasets.keys(), pos_model):
        values = np.atleast_1d(datasets[model].data.flat)
        #         errors = np.atleast_1d(model_std[model])
        color = o2_model_colors()[model]
        # get total number of datapoints for jitter and create shifted positions if more than one member
        n_values = len(values)

        std = np.nanstd(values)
        mean = np.nanmean(values)

        if n_values > 1:
            if bars:
                ax.plot(
                    [mean - std, mean + std],
                    [p_model, p_model],
                    color=color,
                    alpha=alpha,
                    lw=1,
                )
            else:
                pos_jitter = np.random.choice(
                    np.linspace(
                        p_model - member_jitter_amount,
                        p_model + member_jitter_amount,
                        n_values,
                    ),
                    size=n_values,
                    replace=False,
                )

                color = o2_model_colors()[model]
                ax.scatter(
                    values, pos_jitter, color=color, alpha=0.5, edgecolor="none", s=s
                )

        # plot a more distinct mean value
        ax.scatter(
            mean, p_model, color=color, alpha=alpha, edgecolor="none", **kwargs
        )  # edgecolor="k",
        model_member_averaged.append(np.nanmean(values))

    model_member_averaged = np.array(model_member_averaged)
    return model_member_averaged


def o2_model_colors():
    """Returns a color dict for the o2_models"""
    names = o2_models()
    cmap = matplotlib.cm.get_cmap("nipy_spectral")
    # combine several colormaps
    colors = [matplotlib.cm.get_cmap("Accent")(i) for i in np.linspace(0, 1, 8)] + [
        matplotlib.cm.get_cmap("tab10")(i) for i in np.linspace(0, 1, 10)
    ]
    colors = {name: color for name, color in zip(names, colors)}

    # manual changes
    # ACCESS, that is just aweful.
    colors["ACCESS-ESM1-5"] = "teal"
    colors["GFDL-CM4"] = "khaki"
    colors["GFDL-ESM4"] = "gold"
    colors["MPI-ESM1-2-HAM"] = "royalblue"
    colors["MPI-ESM1-2-LR"] = "mediumblue"
    colors["MPI-ESM1-2-HR"] = "cornflowerblue"
    colors["CanESM5"] = "hotpink"
    colors["CanESM5-CanOE"] = "lightpink"
    colors["MIROC-ES2L"] = "darkorchid"
    colors["NorESM1-F"] = "chocolate"
    colors["NorCPM1"] = "sandybrown"
    colors["NorESM2-LM"] = "saddlebrown"
    colors["NorESM2-MM"] = "peru"
    colors["IPSL-CM6A-LR"] = "red"

    return colors


def model_color_legend(
    ax=None, bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.0, models=None, **kwargs
):
    if models is None:
        models = o2_models()
    models = np.sort(models)
    handles = [mpatches.Patch(color=o2_model_colors()[m], label=m) for m in models]
    if ax is None:
        ax = plt.gca()
    ax.legend(
        handles=handles,
        bbox_to_anchor=bbox_to_anchor,
        loc=loc,
        borderaxespad=borderaxespad,
        **kwargs
    )

class ScientificManualFormatter(matplotlib.ticker.ScalarFormatter):
    def __init__(self, order=0, fformat="%1.1f", offset=True, mathText=True):
        self.oom = order
        self.fformat = fformat
        matplotlib.ticker.ScalarFormatter.__init__(
            self, useOffset=offset, useMathText=mathText
        )

    def _set_order_of_magnitude(self):
        self.orderOfMagnitude = self.oom

    def _set_format(self, vmin=None, vmax=None):
        self.format = self.fformat
        if self._useMathText:
            self.format = r"$\mathdefault{%s}$" % self.format
            
            
def polish_map(ax, crs=None, lon_labels='bottom', lat_labels='left', lon_ticks=None, lat_ticks=None, extent=True):
    if crs is None:
        crs = ccrs.PlateCarree()
    map_util_plot(ax, land_color="0.2", labels=True)
    ax.set_aspect(1.5)
    gl = ax.gridlines(
        crs=crs,
        draw_labels=True,
        linewidth=2,
        color="gray",
        alpha=0.5,
        linestyle="--",
    )
    if lon_labels == 'bottom':
        gl.xlabels_bottom = True
        gl.xlabels_top = False
    elif lon_labels == 'top':
        gl.xlabels_bottom = False
        gl.xlabels_top = True
    elif lon_labels is None:
        gl.xlabels_bottom = False
        gl.xlabels_top = False
        
    if lat_labels == 'left':
        gl.ylabels_left = True
        gl.ylabels_right = False
    elif lat_labels == 'right':
        gl.ylabels_left = False
        gl.ylabels_right = True
    elif lat_labels is None:
        gl.ylabels_left = False
        gl.ylabels_right = False
    if lon_ticks:
        gl.xlocator = mticker.FixedLocator(lon_ticks)
    if lat_ticks:
        gl.ylocator = mticker.FixedLocator(lat_ticks)
    
    if extent:
        ax.set_extent([110, 300, -30, 30], crs=crs)