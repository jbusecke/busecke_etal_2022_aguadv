# busecke_etal_2021_aguadv

<!-- [![Build Status](https://github.com/jbusecke/busecke_etal_2021_aguadv/workflows/Tests/badge.svg)](https://github.com/jbusecke/busecke_etal_2021_aguadv/actions) -->
<!-- [![codecov](https://codecov.io/gh/jbusecke/busecke_etal_2021_aguadv/branch/master/graph/badge.svg)](https://codecov.io/gh/jbusecke/busecke_etal_2021_aguadv) -->
[![License:MIT](https://img.shields.io/badge/License-MIT-lightgray.svg?style=flt-square)](https://opensource.org/licenses/MIT)
[![DOI](https://sandbox.zenodo.org/badge/DOI/10.5072/zenodo.1035179.svg)](https://sandbox.zenodo.org/record/1035179)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4742926.svg)](https://doi.org/10.5281/zenodo.4742926)
<!-- [![pypi](https://img.shields.io/pypi/v/busecke_etal_2021_aguadv.svg)](https://pypi.org/project/busecke_etal_2021_aguadv) -->
<!-- [![conda-forge](https://img.shields.io/conda/dn/conda-forge/busecke_etal_2021_aguadv?label=conda-forge)](https://anaconda.org/conda-forge/busecke_etal_2021_aguadv) -->
<!-- [![Documentation Status](https://readthedocs.org/projects/busecke_etal_2021_aguadv/badge/?version=latest)](https://busecke_etal_2021_aguadv.readthedocs.io/en/latest/?badge=latest) -->



The code to reproduce the Figures from our paper submitted to AGU Advances.

## Reproduce our results

### Option 1: Binder


The simplest option. Just click on the button below and execute the notebook when everything is set up.

> Downloading the data and unpacking it can take some time.

[![Binder](https://binder.pangeo.io/badge_logo.svg)](https://binder.pangeo.io/v2/gh/jbusecke/busecke_etal_2021_aguadv/main?filepath=notebooks%2Fbusecke_etal_2021_aguadv_plots.ipynb)

### Option 2: Manually reproduce results
Clone this repository to your machine of choice

Then create the software environment provided in the `environment.yml` file, activate it, and install the paper package
```
$ conda env create -f environment.yml

$ conda activate busecke_etal_2021_aguadv

$ pip install .
```
> This builds the environment with the latest versions of available packages. If you run into trouble or want the exact environment we used, substitute `environment.yml` with `environment.locked.yml` above

Then you can just run `notebooks/busecke_etal_2021_aguadv_plots.ipynb` to reproduce the results.


## Full preprocessing

The code for processing the raw data is found in the more general purpuse [cmip6_omz](https://github.com/jbusecke/cmip6_omz) repository. hese are only reproducible on the princeton [HPC system](https://researchcomputing.princeton.edu/systems/) and are not included due to their sheer size (100TB + for the raw CMIP6 data and still many 100 GBs for the raw processed data).
Notebooks to produce the plotting data (archived on [zenodo]()) can be found in `notebooks/preprocessing/`. T

--------

<p><small>Project based on the <a target="_blank" href="https://github.com/jbusecke/cookiecutter-science-project">cookiecutter science project template</a>.</small></p>
