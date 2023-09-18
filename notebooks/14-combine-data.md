---
jupytext:
  cell_metadata_filter: -run_control,-deletable,-editable,-jupyter,-slideshow
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.15.2
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

<p><font size="6"><b>Stacking of raster data</b></font></p>


> *DS Python for GIS and Geoscience*  
> *November, 2023*
>
> *© 2023, Joris Van den Bossche and Stijn Van Hoey. Licensed under [CC BY 4.0 Creative Commons](http://creativecommons.org/licenses/by/4.0/)*

---

```{code-cell} ipython3
import shutil
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import xarray as xr
```

## Introduction

+++

Geospatial time series data is often stored as multiple individual files. For example, remote sensing data or geoscience model output are typically organized with each time step (or band) in a separate file. Handling all these indidivudal files is culbersome and workflows to combine these files into a single `xarray.Dataset` or `xarray.DataArray` prior to the analysis are required. 

In this notebook, we will explore some ways to combine indidivual files into a single data product ready for analysis.

+++

## Load multiple files into a single `xarray.Dataset/xarray.DataArray`

+++

In some of the previous notebooks, we used the band 4 and band 8 Sentinel image data from Ghent, which are both stored as a separate data file in the `data` directory.

One way to handle this is to load each of the data sets into memory and concatenate these afterwards:

```{code-cell} ipython3
arr_b4 = xr.open_dataarray("data/gent/raster/2020-09-17_Sentinel_2_L1C_B04.tiff", engine="rasterio")
arr_b8 = xr.open_dataarray("data/gent/raster/2020-09-17_Sentinel_2_L1C_B08.tiff", engine="rasterio")
```

```{code-cell} ipython3
band_var = xr.Variable('band', ["B4", "B8"])
arr = xr.concat([arr_b4, arr_b8], dim=band_var)
arr
```

From now on, the data is contained in a single `DataArray` to do further analysis. This approach works just fine for this limited set of data.

However, when more files need to be processed, this becomes labor/code intensive and additional automation is required. Consider the following example data in the data folder `./data/herstappe/raster/sentinel_moisture/`:

```
./data/herstappe/raster/sentinel_moisture/
├── 2016-05-01, Sentinel-2A L1C, Moisture index.tiff
├── 2019-02-15, Sentinel-2A L1C, Moisture index.tiff
└── 2020-02-07, Sentinel-2A L1C, Moisture index.tiff
```

It is a (small) extract of a time series of moisture index data derived from sentinel-2A, made available by [Sentinel-Hub](https://apps.sentinel-hub.com/eo-browser), a time series of remote sensing images. 

Instead of manually loading the data, we rather automate the data load from these files to a single xarray object:

+++

1. Identify all files in the data folder and make a list of them:

```{code-cell} ipython3
from pathlib import Path
moisture_index_files = list(sorted(Path("./data/herstappe/raster/sentinel_moisture").rglob("*.tiff")))
```

2. Extract the time-dimension from each individual file name

```{code-cell} ipython3
moisture_index_dates = [pd.to_datetime(file_name.stem.split(",")[0]) for file_name in moisture_index_files]
moisture_index_dates
```

__Note__ we use `pathlib` instead of `glob.glob` as it returns `Path` objects instead to represent the file names which are more powerful than regular strings returned by `glob.glob`, e.g. usage of `stem` attribute.

+++

3.  Prepare an xarray variable which can be used as the additional date dimension/coordinate

```{code-cell} ipython3
date_var = xr.Variable('date', moisture_index_dates)
date_var
```

4. Load in and concatenate all individual GeoTIFFs

```{code-cell} ipython3
moisture_index = xr.concat(
    [xr.open_dataarray(file_name, engine="rasterio", mask_and_scale=False) for file_name in moisture_index_files],
    dim=date_var
)
```

```{code-cell} ipython3
moisture_index.sortby("date").plot.imshow(col="date", figsize=(15, 4), aspect=1)
```

## Lazy load multiple files into a single `xarray.Dataset`

+++

In the previous example, all data is read into memory. Xarray provides a separate function [`open_mfdataset`](http://xarray.pydata.org/en/stable/generated/xarray.open_mfdataset.html#xarray-open-mfdataset) to read data lazy from disk (so not loading the data itself in memory) from multiple files. 

A usefule feature is the ability to preprocess the files:

> __preprocess (callable(), optional)__ – If provided, call this function on each dataset prior to concatenation. You can find the file-name from which each dataset was loaded in ds.encoding["source"].

Applied to the previous moisture index files example:

```{code-cell} ipython3
def add_date_dimension(ds):
    """Add the date dimension derived from the file_name and rename to moisture_index"""
    ds_date = pd.to_datetime(Path(ds.encoding["source"]).stem.split(",")[0])
    ds = ds.assign_coords(date=("date", [ds_date])).rename({"band_data": "moisture_index"})
    return ds
```

```{code-cell} ipython3
moisture_index_lazy = xr.open_mfdataset(sorted(Path("./data/herstappe/raster/sentinel_moisture").rglob("*.tiff")), 
                                        preprocess=add_date_dimension, engine="rasterio", decode_cf=False) # parallel=True
moisture_index_lazy["moisture_index"]
```

The data itself is not loaded directly and is divided into 3 chunks, i.e. a chunk for each date. See the notebook [15-xarray-dask-big-data](./15-xarray-dask-big-data.ipynb) notebook for more information on the processing of (out of memory) lazy data with Dask.

+++

Further reading:

- See http://xarray.pydata.org/en/stable/user-guide/io.html#reading-multi-file-datasets for more examples.
- https://medium.com/@bonnefond.virginie/handling-multi-temporal-satellite-images-with-xarray-30d142d3391
- https://docs.dea.ga.gov.au/notebooks/Frequently_used_code/Opening_GeoTIFFs_NetCDFs.html#Loading-multiple-files-into-a-single-xarray.Dataset

+++

## Save concatenated data to a single file

+++

After processing multiple files, it is convenient to save the data in a preferred format afterwards. Convenient choices are [NetCDF](https://www.unidata.ucar.edu/software/netcdf/) and [Zarr](https://zarr.readthedocs.io/en/stable/). Zarr is a newer format providing some advantages when working in cloud environments, but can be used on a local machine as well.

```{code-cell} ipython3
moisture_index.to_netcdf("moisture_index_stacked.nc")
```

Hence, the next the data set can be loaded directly from disk:

```{code-cell} ipython3
xr.open_dataset("moisture_index_stacked.nc", engine="netcdf4")
```

Storing to zarr files works on the `xarray.DataSet` level:

```{code-cell} ipython3
moisture_index_lazy.to_zarr("moisture_index_stacked.zarr")
```

```{code-cell} ipython3
xr.open_dataset("moisture_index_stacked.zarr", engine="zarr")    
```

_clean up of these example files_

```{code-cell} ipython3
import shutil

if Path("moisture_index_stacked.zarr").exists():
    shutil.rmtree("moisture_index_stacked.zarr")
if Path("moisture_index_stacked.nc").exists():    
    Path("moisture_index_stacked.nc").unlink()
```

<div class="alert alert-success">

**EXERCISE**:
    
The [NOAA's NCEP Reanalysis data](https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.html) files are stored on a remote server and can be accessed over OpenDAP.
    
> The NCEP/NCAR Reanalysis data set is a continually updated (1948–present) globally gridded data set that represents the state of the Earth's atmosphere, incorporating observations and numerical weather prediction (NWP) model output from 1948 to present.
    
An example can be found in NCEP Reanalysis catalog:

https://www.esrl.noaa.gov/psd/thredds/catalog/Datasets/ncep.reanalysis/surface/catalog.html

The dataset is split into different files for each variable and year. For example, a single file download link for surface air temperature looks like:

https://psl.noaa.gov/thredds/fileServer/Datasets/ncep.reanalysis/surface/air.sig995.1948.nc   
    
The structure is `'http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis/surface/air.sig995.`' + `'YYYY'` + `'.nc'`
    
We want to download the surface temperature data from 1990 till 2000 and combine them all in a single xarray DataSet. To do so:
    
- Prepare all the links by composing the base_url ('http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis/surface/air.sig995') with the required years
- Use the list of file links as the inputfor the `xr.open_mfdataset` to create a single `xarray.DataSet`.
- Whereas this is 600MB of data, the initial loading is not actually reading in the data.
   
<details>
    
<summary>Hints</summary>

* Python works with string formatting, e.g. f'{base_url}.{year}.nc' will nicely create the required links.
* Xarray can both work with file names on a computer as a compatible network link.
* As the netcdf data provided by NOAA is already well structured and confomr, no further adjustments are required as input to the 
`open_mfdataset` function, :-)

</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

base_url = 'http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis/surface/air.sig995'

files = [f'{base_url}.{year}.nc' for year in range(1990, 2001)]
files
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

ds = xr.open_mfdataset(files, parallel=True)
ds
```

## (Optional) Online data Catalogs: STAC

+++

__Note__ _These dependencies are not included in the environment, to run this section, install the required packages first in your conda environment: `conda install stackstac pystac-client`._

+++

Multiple initiatives do exist which publish data online which enables (lazy) loading of the data directly in xarray, such as [OpenDAP](https://www.opendap.org/) and [THREDDS](https://www.unidata.ucar.edu/software/tds/current/) which are well-known and used in the oceanographic and climate studies communities (see exercise). See for example the [ROMS Ocean Model Example](http://xarray.pydata.org/en/stable/examples/ROMS_ocean_model.html) tutorial of xarray. 

Another initiative that interacts well with xarray is the [SpatioTemporal Asset Catalogs](https://stacspec.org/) specification, which is increasingly used to publish remote sensing products.

```{code-cell} ipython3
import stackstac
import pystac_client
```

```{code-cell} ipython3
lon, lat = -105.78, 35.79
```

```{code-cell} ipython3
URL = "https://earth-search.aws.element84.com/v0"
catalog = pystac_client.Client.open(URL)
```

```{code-cell} ipython3
results = catalog.search(
    intersects=dict(type="Point", coordinates=[lon, lat]),
    collections=["sentinel-s2-l2a-cogs"],
    datetime="2020-04-01/2020-05-01"
)
results.matched()
```

```{code-cell} ipython3
list(results.items())[0]
```

```{code-cell} ipython3
results.item_collection()
```

```{code-cell} ipython3
stacked = stackstac.stack(results.item_collection())
```

```{code-cell} ipython3
stacked
```

See also https://github.com/stac-utils/pystac-client and https://stackstac.readthedocs.io/en/latest/.

+++

__Acknowledgements__ Thanks to [@rabernat](https://rabernat.github.io/research_computing_2018/xarray-tips-and-tricks.html) for the example case of NCEP reanalysis data load and https://stackstac.readthedocs.io/en/latest/basic.html#Basic-example for the stackteac example.
