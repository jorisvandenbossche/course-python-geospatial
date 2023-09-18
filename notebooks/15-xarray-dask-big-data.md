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

<p><font size="6"><b>Working with big data: xarray and dask (DEMO)</b></font></p>


> *DS Python for GIS and Geoscience*  
> *November, 2023*
>
> *© 2023, Joris Van den Bossche and Stijn Van Hoey. Licensed under [CC BY 4.0 Creative Commons](http://creativecommons.org/licenses/by/4.0/)*

---

Throughout the course, we worked with small, often simplified or subsampled data. In practice, the tools we have seen still work well with data that fit easily in memory. But also for data larger than memory (e.g. large or high resolution climate data), we can still use many of the familiar tools.

This notebooks includes a brief showcase of using xarray with dask, a package to scale Python workflows (https://dask.org/). Dask integrates very well with xarray, providing a familiar xarray workflow for working with large datasets in parallel or on clusters.

```{code-cell} ipython3
from dask.distributed import Client, LocalCluster
client = Client(LocalCluster(processes=False))  # set up local cluster on your laptop
client
```

The *Multi-Scale Ultra High Resolution (MUR) Sea Surface Temperature (SST)* dataset (https://registry.opendata.aws/mur/) provides freely available, global, gap-free, gridded, daily, 1 km data on sea surface temperate for the last 20 years. I downloaded a tiny part this dataset (8 days of 2020) to my local laptop, and stored a subset of the variables (only the "sst" itself) in the zarr format (https://zarr.readthedocs.io/en/stable/), so we can efficiently read it with xarray and dask:

```{code-cell} ipython3
import xarray as xr
```

```{code-cell} ipython3
ds = xr.open_zarr("data/mur_sst_zarr/")
```

```{code-cell} ipython3
ds
```

Looking at the actual sea surface temperature DataArray:

```{code-cell} ipython3
ds.analysed_sst
```

The representation already indicated that this DataArray (although being a tiny part of the actual full dataset) is quite big: 20.7 GB if loaded fully into memory at once (which would not fit in the memory of my laptop).

The xarray.DataArray is now backed by a dask array instead of a numpy array. This allows us to do computations on the large data in *chunked* way.

+++

For example, let's compute the overall average temperature for the full globe for each timestep:

```{code-cell} ipython3
overall_mean = ds.analysed_sst.mean(dim=("lon", "lat"))
overall_mean
```

This returned a lazy object, and not yet computed the actual average. Let's explicitly compute it:

```{code-cell} ipython3
%%time 
overall_mean.compute()
```

This takes some time, but it *did* run on my laptop even while the dataset did not fit in the memory of my laptop.

+++

Integrating with hvplot and datashader, we can also still interactively plot and explore the large dataset:

```{code-cell} ipython3
import hvplot.xarray
```

```{code-cell} ipython3
ds.analysed_sst.isel(time=-1).hvplot.quadmesh(
    'lon', 'lat', rasterize=True, dynamic=True,
    width=800, height=450, cmap='RdBu_r')
```

Zooming in on this figure we re-read and rasterize the subset we are viewing to provide a higher resolution image.

+++

**As a summary**, using dask with xarray allows:

- to use the familiar xarray workflows for larger data as well
- use the same code to work on our laptop or on a big cluster

+++

---

# PANGEO: A community platform for Big Data geoscience


<center><img src="https://pangeo.io/_images/pangeo_simple_logo.svg" width="500px"></center>

Website: https://pangeo.io/index.html

They have a gallery with many interesting examples, many of them using this combination of xarray and dask.

Pangeo focuses primarily on *cloud computing* (storing the big datasets in cloud-native file formats and also doing the computations in the cloud), but all the tools like xarray and dask developed by this community and shown in the examples also work on your laptop or university's cluster.


<img src="https://pangeo.io/_images/pangeo_tech_1.png" width="800px">

```{code-cell} ipython3

```
