import socket
import pathlib
import xarray as xr
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker
import regionmask
from cmip6_preprocessing.regionmask import merged_mask
from cmip6_preprocessing.utils import cmip6_dataset_id
from fastprogress import progress_bar
from xarrayutils.utils import linear_trend
import xesmf as xe

hist_slice = slice('1950', '2000')
trend_slice = slice('2000', '2100')


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


def load_zarr_directory(path, pattern='*.zarr', zarr_kwargs={}):
    """Convenience function to read CMIP6 data"""
    zarr_kwargs.setdefault('use_cftime', True)
    zarr_kwargs.setdefault('consolidated', True)
    if not isinstance(path, pathlib.Path):
        path = pathlib.Path(path)
    flist = list(path.glob(pattern))
    # TODO Can I accelerate this with dask.delayed?
    datasets = []
    for f in progress_bar(flist):
        datasets.append(xr.open_zarr(f, **zarr_kwargs))
    # convert to cmip6 dict
    return {cmip6_dataset_id(ds):ds for ds in datasets}

# def read_files(
#     ddir,
#     pattern="*.nc",
#     sep="_",
#     models=o2_models(), # this should go and just scan all files
#     experiments=["historical", "ssp585"],
#     read_chunks={"time": 10, "memebr_id": 1},
#     verbose=False,
# ):
#     """Scans `ddir` and loads/parses datasets into a nested dictionary of xarray datasets"""
#     if not isinstance(ddir, pathlib.Path):
#         ddir = pathlib.Path(ddir)

#     filelist = list(ddir.glob(pattern))
#     if len(filelist) == 0:
#         print(f"No files found for pattern:{pattern} in {str(ddir)}")
#         return None
#     else:
#         datadict = {}
#         for model in models:
#             if verbose:
#                 print(model)
#             # need to add the sep variables, or else some models (CanESM get double counted)
#             model_filelist = [f for f in filelist if sep + model + sep in str(f)]
#             if len(model_filelist) > 0:
#                 datadict[model] = {}
#                 for experiment in experiments:
#                     experiment_filelist = [
#                         f for f in model_filelist if experiment in str(f)
#                     ]
#                     if len(experiment_filelist) > 0:
#                         if verbose:
#                             print(len(experiment_filelist))
#                         # Build an option for zarrs once I need it.
#                         # find out which chunks to apply
#                         ds_test = xr.open_dataset(experiment_filelist[0])
#                         chunks = {
#                             k: v for k, v in read_chunks.items() if k in ds_test.dims
#                         }

#                         datasets = [
#                             xr.open_dataset(f, chunks=chunks)
#                             for f in experiment_filelist
#                         ]  # ,
#                         # not sure if this is the most general, but for now it should work...
#                         ds = xr.concat(
#                             datasets,
#                             dim="member_id",
#                             compat="override",
#                             coords="minimal",
#                         )
#                         # replace some attrs (!!! This should actually be done upstream)
#                         ds.attrs["source_id"] = model
#                         ds.attrs["experiment_id"] = experiment
#                         datadict[model][experiment] = ds
#                     else:
#                         print(
#                             f"No files found for model:{model} experiment:{experiment}"
#                         )

#             else:
#                 print(f"No files found for model:{model}")
#         return datadict
    
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

def fail_age(ds):
    """Returns False if dataset was deemed unusable"""
    # TODO: Make this not some of the most embarrising code I have ever written....
    fail_attrs = [
        {'source_id':'MPI-ESM1-2-LR', 'variant_label':'r10i1p1f1'},
        {'source_id':'MPI-ESM1-2-LR', 'variant_label':'r8i1p1f1'},
        {'source_id':'MPI-ESM1-2-LR', 'variant_label':'r9i1p1f1'},
        {'source_id':'MRI-ESM2-0', 'variant_label':'all'},
        {'source_id':'MPI-ESM1-2-HR', 'variant_label':'all'},
    ]
    check = []
    for fa in fail_attrs:
        subcheck = []
        for k_fail,v_fail in fa.items():
            
            v = ds.attrs.get(k_fail)
            if (v_fail == v) or (v_fail=='all'):
                subcheck.append(True)
            else:
                subcheck.append(False)
        check.append(all(subcheck))
        
    check = any(check)
    return check

def slope(da):
    """returns slope per century"""
    assert len(da.time) < 300 # make sure the data is annual
    assert len(da.time)> 95 # make sure this covers most of the century allows for small adjustments 
    reg = linear_trend(da.sel(time=trend_slice), 'time')
    return reg.slope * 100, reg.p_value 




def regrid(ds, dlon=1, dlat=1):
    target_grid = xe.util.grid_global(dlon, dlat)
    regridder = xe.Regridder(
        ds, target_grid, "bilinear", periodic=True, ignore_degenerate=True, unmapped_to_nan=True
    )
    ds_out = regridder(ds)
    ds_out = ds_out.assign_coords(x=ds_out.lon.isel(y=0).data, y=ds_out.lat.isel(x=0).data)
    ds_out.attrs = {k:v for k,v in ds.attrs.items() if k not in ['grid_label']}
    return ds_out

def member_treatment(ds):
    
    # average members
    if 'member_id' not in ds.dims:
        ds = ds.expand_dims('member_id')

    averaged_members = len(ds.member_id)
    member_ids = ds.member_id.data
    ds = ds.mean('member_id')
    
    return ds, averaged_members, member_ids

def cut_long_members(ds):
    """Cut members beyong 2100 to avoid issues with dask chunking"""
    if 'time' in ds.dims:
        ds = ds.sel(time=slice(None, '2100'))
    return ds


#### filter out datasets with unexpected length (this should probably go to cmip6_preprocessing?)
import warnings

def _expected_length(ds):
    if ds.experiment_id == "historical":
        if ds.table_id == "Omon":
            return 1980
        else:
            warnings.warn(
                f"unknown table_id [{ds.table_id}] for {cmip6_dataset_id(ds)}"
            )
            return 1

    elif "ssp" in ds.experiment_id:
        if ds.table_id == "Omon":
            return 1032
        else:
            warnings.warn(
                f"unknown table_id [{ds.table_id}] for {cmip6_dataset_id(ds)}"
            )
            return 1

    elif "Control" in ds.experiment_id:
        if ds.table_id == "Omon":
            return (
                12 * 50
            )  # just give a low number here so none of the controls are dropped
        else:
            warnings.warn(
                f"unknown table_id [{ds.table_id}] for {cmip6_dataset_id(ds)}"
            )
            return 1
    else:
        warnings.warn(
            f"unknown experiment_id [{ds.experiment_id}] for {cmip6_dataset_id(ds)}"
        )
        return 1


def drop_short_long_datasets(ddict):
    """Filters a dictionary of xarray datasets and drops datasets that do not have the expected length.
    This is mostly relevant for metrics, which sometimes are not complete in time."""
    ddict_filtered = {}
    for name, ds in ddict.items():
        # drop everything but main variable
        ds = ds.drop([v for v in ds.data_vars if v != ds.variable_id])
        # remove any output in density coordinates (Nor ESM?)
        if not 'rho' in ds.dims:
            # filter out too short runs
            if "time" not in ds.dims:
                ddict_filtered[name] = ds
            else:
                if len(ds.time) < _expected_length(ds):
                    print("---------DROPPED--------")
                    print(name)
                    print(_expected_length(ds))
                    print(len(ds.time))
                    print("---------DROPPED--------")
                else:
                    ddict_filtered[name] = ds
    return ddict_filtered