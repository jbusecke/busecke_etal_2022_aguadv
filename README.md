# busecke_etal_2022_aguadv
| | |
| ----- | ------- |
| License | [![License:MIT](https://img.shields.io/badge/License-MIT-lightgray.svg?style=flt-square)](https://opensource.org/licenses/MIT) |
| Data  | [![Data](https://zenodo.org/badge/DOI/10.5281/zenodo.6799335.svg)](https://doi.org/10.5281/zenodo.6799335) |
| Code |[![Software](https://zenodo.org/badge/DOI/10.5281/zenodo.6803919.svg)](https://doi.org/10.5281/zenodo.6803919)|




The code to reproduce the Figures from our paper submitted to AGU Advances.

## Reproduce our results

### Option 1: Binder


The simplest option. Just click on the button below and execute the notebook when everything is set up.

> Downloading the data and unpacking it can take some time.

[![Binder](https://binder-staging.2i2c.cloud/badge_logo.svg)](https://binder-staging.2i2c.cloud/v2/gh/jbusecke/busecke_etal_2022_aguadv/main?labpath=notebooks%2Fplots.ipynb)

### Option 2: Manually reproduce results
Clone this repository to your machine of choice

Then create the software environment provided in the `environment.yml` file, activate it, and install the paper package
```
$ conda env create -f environment.yml

$ conda activate busecke_etal_2022_aguadv

$ pip install .
```
> This builds the environment with the latest versions of available packages. If you run into trouble or want the exact environment we used, substitute `environment.yml` with `environment.locked.yml` above

Then you can just run `notebooks/plots.ipynb` to reproduce the results.


## Full preprocessing

The code for processing the raw data is found in the more general purpuse [cmip6_omz](https://github.com/jbusecke/cmip6_omz) repository. hese are only reproducible on the princeton [HPC system](https://researchcomputing.princeton.edu/systems/) and are not included due to their sheer size (100TB + for the raw CMIP6 data and still many 100 GBs for the raw processed data).
Notebooks to produce the plotting data (archived on [zenodo]()) can be found in `notebooks/preprocessing/`. T

--------

<p><small>Project based on the <a target="_blank" href="https://github.com/jbusecke/cookiecutter-science-project">cookiecutter science project template</a>.</small></p>
