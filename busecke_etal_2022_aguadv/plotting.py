import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker

import cartopy.crs as ccrs
from busecke_etal_2022_aguadv.utils import o2_models
from xarrayutils.plotting import map_util_plot


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
            
    
def polish_map(
    ax,
    crs=None,
    lon_labels='bottom',
    lat_labels='left',
    lon_ticks=None,
    lat_ticks=None,
    extent=[115, 305, -40, 50],
    aspect=False
):
    if crs is None:
        crs = ccrs.PlateCarree()
    map_util_plot(ax, land_color="0.2", labels=True)
    if aspect:
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
        ax.set_extent(extent, crs=crs)
        
        
def mask_multi_model(da, dim='model'):
    """Mask out areas where only few of the models have values"""
    return np.isnan(da).sum(dim)<4.5
