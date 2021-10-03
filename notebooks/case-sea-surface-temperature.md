---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.12.0
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

<p><font size="6"><b>CASE - Sea Surface Temperature data</b></font></p>


> *DS Python for GIS and Geoscience*  
> *October, 2021*
>
> *© 2021, Joris Van den Bossche and Stijn Van Hoey. Licensed under [CC BY 4.0 Creative Commons](http://creativecommons.org/licenses/by/4.0/)*

---

```{code-cell} ipython3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import xarray as xr
```

For this use case, we focus on the [Extended Reconstructed Sea Surface Temperature (ERSST)](https://www.ncdc.noaa.gov/data-access/marineocean-data/extended-reconstructed-sea-surface-temperature-ersst-v4), a widely used and trusted gridded compilation of historical Sea Surface Temperature (SST).

> The Extended Reconstructed Sea Surface Temperature (ERSST) dataset is a global monthly sea surface temperature dataset derived from the International Comprehensive Ocean–Atmosphere Dataset (ICOADS). It is produced on a 2° × 2° grid with spatial completeness enhanced using statistical methods. This monthly analysis begins in January 1854 continuing to the present and includes anomalies computed with respect to a 1971–2000 monthly climatology. 



First we download the dataset. We will use the [NOAA Extended Reconstructed Sea Surface Temperature (ERSST)](https://psl.noaa.gov/thredds/catalog/Datasets/noaa.ersst/catalog.html?dataset=Datasets/noaa.ersst/sst.mnmean.v4.nc) v4 product. Download the data from this link: https://psl.noaa.gov/thredds/fileServer/Datasets/noaa.ersst/sst.mnmean.v4.nc and store it in a subfolder `data/` from the notebook as `sst.mnmean.v4.nc`.

+++

Reading in the data set, ignoring the `time_bnds` variable:

```{code-cell} ipython3
data = './data/sst.mnmean.v4.nc'
ds = xr.open_dataset(data, drop_variables=['time_bnds'], engine="h5netcdf")
```

For this use case, we will focus on the years after 1960, so we slice the data from 1960 and load the data into our computer memory. By only loading the data after the initial slice, we make sure to only load into memory the data we specifically need:

```{code-cell} ipython3
ds = ds.sel(time=slice('1960', '2018')).load()  # load into memory
ds
```

The data with the extension `nc` is a NetCDF format. NetCDF (Network Common Data Format) is the most widely used format for distributing geoscience data. NetCDF is maintained by the [Unidata](https://www.unidata.ucar.edu/) organization. Check the [netcdf website](https://www.unidata.ucar.edu/software/netcdf/docs/faq.html#whatisit) for more information. Xarray was designed to make reading netCDF files in python as easy, powerful, and flexible as possible.

+++

__Note:__ As the data is in a [OPeNDAP server](https://en.wikipedia.org/wiki/OPeNDAP), we could also load the NETCDF data directly without downloading anything. This would require us to add the `netcdf4` package in our conda environment

+++

### Exploratory data analysis

+++

The data contains a single data variable `sst` and has 3 dimensions: lon, lat and time each described by a coordinate. Let's first get some insight in the structure and content of the data.

+++

<div class="alert alert-success">

**EXERCISE**:

- What is the total amount of elements/values in the xarray data set?
- How many elements are there in the different dimensions   
- The metadata of a netcdf file is also interpreted by xarray. Are the attributes on the xarray.Dataset `ds` the same as the attributes of the `sst` data itself?
   
<details>

<summary>Hints</summary>
    
- The number of elements or `size` of an array is an attribute of an xarray.DataArray and not of a xarray.Dataset
- Also the `shape` of an array is an attribute of an xarray.DataArray. A xarray.Dataset has the `dims` attribute to query dimension sizes

</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

# size attribute of array object
ds["sst"].size
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# shape attribute of array object
ds["sst"].shape
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# dims attribute of dataset object
ds.dims
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# attributes of array
ds["sst"].attrs
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# attributes of data set
ds.attrs
```

---------

+++

As we work with a single data variable, we will introduce a new variable `sst` which is the `xarray.DataArray` of the SST values. Note that we only keep the attributes on the xarray.DataArray level.

```{code-cell} ipython3
sst = ds["sst"]
```

```{code-cell} ipython3
sst
```

<div class="alert alert-success">

**EXERCISE**:

Make an image plot of the SST in the first month of the data set, January 1960. Adjust the range of the colorbar and switch to the `coolwarm` colormap.
   
<details>

<summary>Hints</summary>
    
- xarray can interpret a date string in the [ISO 8601](https://nl.wikipedia.org/wiki/ISO_8601) format as a date, e.g. `2020-01-01`.
- adjust ranges of the colorbar with `vmin` and `vmax`.

</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

sst.sel(time="1960-01-01").plot.pcolormesh(vmin=-2, vmax=30, 
                                           cmap="coolwarm")
```

__Note__ 
xaray uses xarray.plot.pcolormesh() as the default two-dimensional plot method because it is more flexible than xarray.plot.imshow(). However, for large arrays, imshow can be much faster than pcolormesh. If speed is important to you and you are plotting a regular mesh, consider using imshow.

+++

<div class="alert alert-success">

**EXERCISE**:
    
How did the SST evolve in time for a specific location on the earth? Make a line plot of the SST at `lon=300`, `lat=50` as a function of time.
    
Do you recognize the seasonality of the data?
   
<details>

<summary>Hints</summary>
    
- Use the `sel` for both the lon/lat selection.

</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

sst.sel(lon=300, lat=50).plot.line();
```

<div class="alert alert-success">

**EXERCISE**:

What is the evolution of the SST as function of the month of the year?
    
Calculate the average SST with respect to the _month of the year_ for all positions in the data set and store the result as a variable `ds_mm`.

Use the `ds_mm` variable to make a plot: For longitude `164`, make a comparison in between the monthly average at latitude `-23.4` versus latitude `23.4`. Use a line plot with in the x-axis the month of the year and in the y-axis the average SST.
   
<details>

<summary>Hints</summary>
    
- Use the `sel` for both the lon/lat selection.
- If the exact values are not in the coordinate, you can use the `method="nearest"` inside a selection.

</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

ds_mm = sst.groupby(sst.time.dt.month).mean(dim='time')
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

ds_mm.sel(lon=164, lat=[-23.4, 23.4], method="nearest").plot.line(hue="lat");
```

<div class="alert alert-success">

**EXERCISE**:
    
How does the zonal mean climatology for each month of the year changes with the latitude? 

Reuse the `ds_mm` from the previous exercise or recalculate the average SST with respect to the _month of the year_ for all positions in the data set and store the result as a variable `ds_mm`.
    
To check the mean climatology (aggregating over the longitudes) as a function of the latitude for each month in the year, calculate the average SST over the `lon` dimension from `ds_mm`. Plot the result as an image with the month of the year in the x-axis and the latitude in the y-axis. 
   
<details>

<summary>Hints</summary>

- You do not need another `groupby`, but need to calculate a reduction along a dimension.

</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

ds_mm = sst.groupby(sst.time.dt.month).mean(dim='time')
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

ds_mm.mean(dim='lon').plot.imshow(x="month", y="lat", vmin=-2, vmax=30, cmap="coolwarm")
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# alternative using transpose instead of defining the x and y in the plot function
ds_mm.mean(dim='lon').transpose().plot.imshow(vmin=-2, vmax=30, cmap="coolwarm")
```

<div class="alert alert-success">

**EXERCISE**:
    
How different is the mean climatology in between January and July?

Reuse the `ds_mm` variable from the previous exercises or recalculate the average SST with respect to the _month of the year_ for all positions in the data set and store the result as a variable `ds_mm`.
    
Calculate the difference of the mean climatology between January an July and plot the result as an image (map) with the longitude of the year in the x-axis and the latitude in the y-axis. 
   
<details>

<summary>Hints</summary>

- You can subtract xarray just as Numpy arrays. You do not need another `groupby`, but only selections from the `ds_mm` variable. 

</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

(ds_mm.sel(month=1) - ds_mm.sel(month=7)).plot.imshow(vmax=10)
```

### Calculate the residual by removing climatology

+++

To understand how the SST temperature evolved as a function of time during the last decades, we want to remove this climatology from the dataset and examine the residual, called the anomaly, which is the interesting part from a climate perspective. 

We will do this by subtracting the monthly average from the values of that specific month. Hence, subtract the average January value over the years from the January data, subtract the average February value over the years from the February data,...

Removing the seasonal climatology is an example of a transformation: it operates over a group, but does not change the size of the dataset as we do the operation on each element (`x - x.mean()`) 

This is not the same as the aggregations (e.g. `average`) we applied on each of the groups earlier. When using `groupby`, a calculation to the group can be applied and just like in Pandas, these calculations can either be:

- _aggregation_: reduces the size of the group
- _transformation_: preserves the groups full size

One way to consider is that we `apply` a function to each of the groups. For our anomaly calculation we want to do a _transformation_ and apply the following function:

```{code-cell} ipython3
def remove_time_mean(x):
    """Subtract each value by the mean over time"""
    return x - x.mean(dim='time')
```

We can `apply` this function to each of the groups:

```{code-cell} ipython3
sst = ds["sst"]
ds_anom = sst.groupby('time.month').apply(remove_time_mean)
ds_anom
```

In other words: 

> subtract each element by the average over time of all elements of the month the element belongs to

+++

Xarray makes these sorts of transformations easy by supporting groupby arithmetic. This concept is easiest explained by applying it for our application:

```{code-cell} ipython3
gb = sst.groupby('time.month')  # make groups (in this example each month of the year is a group) 
ds_anom = gb - gb.mean(dim='time')  # subtract each element of the group/month by the mean of that group/month over time 
ds_anom
```

Now we can view the climate signal without the overwhelming influence of the seasonal cycle:

```{code-cell} ipython3
ds_anom.sel(lon=300, lat=50).plot.line()
```

Check the difference between Jan. 1 2018 and Jan. 1 1960 to see where the evolution in time is the largest:

```{code-cell} ipython3
(ds_anom.sel(time='2018-01-01') - ds_anom.sel(time='1960-01-01')).plot()
```

<div class="alert alert-success">

**EXERCISE**:
    
Compute the _five-year median_ of the `ds_anom` variable for the location `lon=300`, `lat=50` as well as the 12 month rolling median of the same data set. Store the output as respectively `ds_anom_resample` and `ds_anom_rolling`.
    
Make a line plot as a function of time for the location `lon=300`, `lat=50` of the original `ds_anom` data, the resampled data and the rolling median data.
   
<details>

<summary>Hints</summary>

- If you only need a single location, do the slicing (selecting) first instead of calculating them for all positions.
- Use the `resample` and the `rolling` functions.


</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

# slice the point of interest
ds_anom_loc = ds_anom.sel(lon=300, lat=50)
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# compute the resampling and rolling
ds_anom_resample = ds_anom_loc.resample(time='5Y').median(dim='time')
ds_anom_rolling = ds_anom_loc.rolling(time=12, center=True).median()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# make a combined plot
fig, ax = plt.subplots()
ds_anom_loc.plot.line(ax=ax, label="monthly anom")
ds_anom_resample.plot.line(marker='o', label="5 year resample")
ds_anom_rolling.plot.line(label='12 month rolling mean')
fig.legend(loc="upper center", ncol=3)
ax.set_title("");
```

### Make projection aware maps

+++

The previous maps were the default outputs of xarray without specification of the spatial context. For reporting these plots are not appropriate. We can use the [cartopy](https://scitools.org.uk/cartopy/docs/latest/) package to adjust our Matplotlib axis to make them spatially aware. 

For more in-depth information on cartopy, see the [visualization-03-cartopy](./visualization-03-cartopy.ipynb) notebook. As a short recap, to make sure the data of xarray can be integrated in a cartopy plot, the crucial element is to define the `transform` argument to to control which coordinate system that the given data is in. You can add the transform keyword with an appropriate `cartopy.crs.CRS` instance from the `import cartopy.crs` module:

```{code-cell} ipython3
import cartopy.crs as ccrs
import cartopy

map_proj = ccrs.Robinson()  # Define the projection

fig, ax = plt.subplots(figsize = (16,9), subplot_kw={"projection": map_proj})
ax.gridlines()
ax.coastlines()

sst.sel(time="1960-01-01").plot(ax=ax, vmin=-2, vmax=30,  center=5,
                                cmap='coolwarm', transform = ccrs.PlateCarree(), # tranform argument
                                cbar_kwargs={'shrink':0.75})
```

<div class="alert alert-success">

**EXERCISE**:
    
Make a plot of the `ds_anom` variable of 2018-01-01 with cartopy.
    
- Use the `ccrs.Orthographic` with the central lon/lat on -20, 5
- Add coastlines and gridlines to the plot    
   
   
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

map_proj = ccrs.Orthographic(-20, 5)

fig, ax = plt.subplots(figsize = (12, 6), subplot_kw={"projection": map_proj})

ax.gridlines()
ax.coastlines()
ds_anom.sel(time='2018-01-01').plot(ax=ax, vmin=-1.5, vmax=1.5,
                                   cmap='coolwarm', transform = ccrs.PlateCarree(),
                                   cbar_kwargs={'shrink':0.5, 'label': 'anomaly'})
```

### Spatial aggregate per basin

+++

Apart from aggregations as a function of time, also spatial aggregations using other (spatial) data sets can be achieved. In the next section, we want to compute the average SST over different ocean basins. The http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NODC/.WOA09/.Masks/.basin/ is a data set that contains the main ocean basins in lon/lat:

```{code-cell} ipython3
basin = xr.open_dataset("./data/basin.nc")
basin = basin.rename({'X': 'lon', 'Y': 'lat'})
basin["basin"]
```

The name of the basins are included in the attributes of the data set. Using Pandas, we can create a mapping in between the basin names and the index used in the basin data set:

```{code-cell} ipython3
basin_names = basin["basin"].attrs['CLIST'].split('\n')
basin_s = pd.Series(basin_names, index=np.arange(1, len(basin_names)+1))
basin_s = basin_s.rename('basin')
basin_s.head()
```

We will use this mapping from identifier to label later in the analysis.

+++

The basin data set provides multiple Z levels. We are interested in the division on surface level (0.0):

```{code-cell} ipython3
basin_surface = basin["basin"].sel(Z=0.0).drop_vars("Z")
basin_surface.plot(vmax=10, cmap='tab10')
```

The next step is to align both data sets. For this application, using the 'nearest' available data point will work to map both data sets with each other. Xarray provides the function `interp_like` to interpolate the `basin_surface` to the `sst` variable:

```{code-cell} ipython3
basin_surface_interp = basin_surface.interp_like(sst, method='nearest')
basin_surface_interp.plot(vmax=10, cmap='tab10')
```

<div class="alert alert-success">

**EXERCISE**:

Compute the mean SST (over all dimensions) for each of the basins in the `basin_surface` variable starting from the `sst` variable. 

Next, we want to plot a horizontal bar chart with the SST for each bar chart. To do so:
    
- Convert the output to Pandas DataFrame.
- Combine the output with the `basin_s` variable by merging on the index (identifiers of the basin names).
- Create a horizontal barplot of the average temperature for each of the basins using the resulting dataframe.
   
<details>

<summary>Hints</summary>

- Use a `groupby` with the `basin_surface_interp` as input.
- Joining and merging of tables? See the [Pandas documentation](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.merge.html). 

</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

basin_mean_sst = sst.groupby(basin_surface_interp).mean()
basin_mean_sst = basin_mean_sst.mean(dim="time")
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# In such a situation, the ELLIPSIS can be used to aggregate over all dimensions
basin_mean_sst = sst.groupby(basin_surface_interp).mean(dim=...) # ellipsis is shortcut for all dimensions
basin_mean_sst
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Convert to a Pandas DataFrame:
basin_mean_df = basin_mean_sst.to_dataframe()
basin_mean_df
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Merge the data with the `basin_s` data on the index:
basin_mean_df_merged = pd.merge(basin_mean_df, basin_s, left_index=True, right_index=True)
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Create a bar chart of the SST per basin data:
basin_mean_df_merged.sort_values(by="sst").plot.barh(x="basin");
```

-------

Acknowledgements to https://earth-env-data-science.github.io/lectures/xarray/xarray-part2.html
