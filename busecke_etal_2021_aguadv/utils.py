import socket
import pathlib
import xarray as xr
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker
import regionmask
from cmip6_preprocessing.regionmask import merged_mask

def o2_models():
    """A central place to store all available models with o2 output"""
    return [
        "CanESM5-CanOE",
        "CanESM5",
        "CNRM-ESM2-1",
        "ACCESS-ESM1-5",
        "IPSL-CM6A-LR",
        "MIROC-ES2L",
        "UKESM1-0-LL",
        "MPI-ESM1-2-HR",
        "MPI-ESM1-2-LR",
        "MRI-ESM2-0",
        "NorESM2-LM",
        "NorESM2-MM",
        "GFDL-CM4",
        "GFDL-ESM4",
    ]

def mask_basin(ds, region='Pacific', drop=True):
    if regionmask is None:
        raise RuntimeError("Please install the latest regionmask version")
    basins = regionmask.defined_regions.natural_earth.ocean_basins_50
    mask = merged_mask(basins, ds)
    masks = {
        'Pacific':np.logical_or(mask == 2, mask == 3),
        'Atlantic':np.logical_or(mask == 0, mask == 1),
        'Indian':mask == 5,  # Indian without Maritime Continent
        'Global': mask >= 0
    }
    ds_masked = ds.where(masks[region], drop=drop)
    return ds_masked

def region(ds, region='Pacific', lat=30):
    ds = mask_basin(ds, region=region)
    ds = ds.where(abs(ds.lat) <= lat, drop=True)
    return ds

def omz_volume(ds):
    da = (ds.omz_thickness * ds.areacello).sum(["x", "y"])
    # some members/models have 0 values. Mask with nan
    da = da.where(da > 0)
    return da

def convert_mol_m3_mymol_kg(o2, rho_0=1025):
    converted = o2 / rho_0 * 1e6
    converted.attrs["units"] = "$\mu mol/kg$"
    return converted

def stci(ds):
    """Calculate the Subtropical Cell Index (STCI) according to Duteil et al. 2014

    Parameters
    ----------
    ds : xr.Dataset
        Input dataset. Needs to have a variable `psi` which represents the meridional mass overturning streamfunction

    Returns
    -------
    xr.Dataset
        The STCI
    """
    dims = ["y", "lev_outer"]
    region = ds.psi.sel(lev_outer=slice(0, 250), y=slice(-10, 10))
    return region.max(dims) - region.min(dims)


def read_files(
    ddir,
    pattern="*.nc",
    sep="_",
    models=o2_models(), # this should go and just scan all files
    experiments=["historical", "ssp585"],
    read_chunks={"time": 10, "memebr_id": 1},
    verbose=False,
):
    """Scans `ddir` and loads/parses datasets into a nested dictionary of xarray datasets"""
    if not isinstance(ddir, pathlib.Path):
        ddir = pathlib.Path(ddir)

    filelist = list(ddir.glob(pattern))
    if len(filelist) == 0:
        print(f"No files found for pattern:{pattern} in {str(ddir)}")
        return None
    else:
        datadict = {}
        for model in models:
            if verbose:
                print(model)
            # need to add the sep variables, or else some models (CanESM get double counted)
            model_filelist = [f for f in filelist if sep + model + sep in str(f)]
            if len(model_filelist) > 0:
                datadict[model] = {}
                for experiment in experiments:
                    experiment_filelist = [
                        f for f in model_filelist if experiment in str(f)
                    ]
                    if len(experiment_filelist) > 0:
                        if verbose:
                            print(len(experiment_filelist))
                        # Build an option for zarrs once I need it.
                        # find out which chunks to apply
                        ds_test = xr.open_dataset(experiment_filelist[0])
                        chunks = {
                            k: v for k, v in read_chunks.items() if k in ds_test.dims
                        }

                        datasets = [
                            xr.open_dataset(f, chunks=chunks)
                            for f in experiment_filelist
                        ]  # ,
                        # not sure if this is the most general, but for now it should work...
                        ds = xr.concat(
                            datasets,
                            dim="member_id",
                            compat="override",
                            coords="minimal",
                        )
                        # replace some attrs (!!! This should actually be done upstream)
                        ds.attrs["source_id"] = model
                        ds.attrs["experiment_id"] = experiment
                        datadict[model][experiment] = ds
                    else:
                        print(
                            f"No files found for model:{model} experiment:{experiment}"
                        )

            else:
                print(f"No files found for model:{model}")
        return datadict
    
def maybe_unpack_date(date):
    """Optionally Extracts the data value of a 1 element xarray datarray."""
    # I should probably not do this here but instead in the higher level functions...
    if isinstance(date, xr.DataArray):
        date = date.data.tolist()
        if isinstance(date, list):
            if len(date) != 1:
                raise RuntimeError(
                    "The passed date has the wrong format. Got [{date}] after conversion to list."
                )
            else:
                date = date[0]
    return date    

def replace_time(ds, ref_date, start_idx=0, freq="1MS", calendar=None):
    """This function replaces the time encoding of a dataset acoording to `ref_date`.
    The ref date can be any index of ds.time (default is 0; meaning the first timestep of ds will be replaced with `ref_date`).
    """
    ds = ds.copy()

    ref_date = maybe_unpack_date(ref_date)

    # determine the start date
    # propagate the date back (this assumes stricly monthly data)

    year = ref_date.year - (start_idx // 12)
    month = ref_date.month - (start_idx % 12)

    if month <= 0:
        # move the year one more back
        year -= 1
        month = 12 + month

    attrs = ds.time.attrs

    start = f"{int(year):04d}-{int(month):02d}"
    #     calendar = ds.attrs.get('calendar_type', None)
    if calendar is None:
        calendar = _get_calendar(ds.time)
        if calendar is None:
            calendar = ds.attrs.get(
                "calendar", "standard"
            )  # !!! this is not great. I should preprocess this and make sure I dont get mixed calendars
    ds = ds.assign_coords(
        time=xr.cftime_range(start, periods=len(ds.time), freq=freq, calendar=calendar)
    )
    ds.time.attrs = attrs
    return ds