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

<p><font size="6"><b>Xarray advanced</b></font></p>


> *DS Python for GIS and Geoscience*  
> *October, 2021*
>
> *© 2021, Joris Van den Bossche and Stijn Van Hoey. Licensed under [CC BY 4.0 Creative Commons](http://creativecommons.org/licenses/by/4.0/)*

---

+++

https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land-monthly-means?tab=overview

```{code-cell} ipython3
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
```

## Meet `xarray.Dataset`

+++

We already know `xarray.DataArray`, it is a single multi-dimensional array and each dimension can have a name and coordinate values. Next to the `DataArray`, `xarray` has a second main data structure to store arrays, i.e. `xarray.DataSet`. 

Let's read an xarray data set (global rain/temperature coverage stored in the file `2016-2017_global_rain-temperature.nc`), using the function `open_dataset`:

```{code-cell} ipython3
ds = xr.open_dataset("./data/2016-2017_global_rain-temperature.nc")
ds
```

<div class="alert alert-info" style="font-size:120%">

**REMEMBER**: <br>

xarray provides reading function for different formats. For GIS formats such as geotiff and other GDAL readable raster data, 
the `open_rasterio` function is available. NetCDF-alike data formats can be loaded using the by `open_dataset` function.

</div>

+++

Let's take a closer look at this `xarray.Dataset`:

- A `xarray.Dataset` is the second main data type provided by xarray
- This example has 3 __dimensions__:
    - `y`: the y coordinates of the data set
    - `x`: the x coordinates of the data set
    - `year`: the year coordinate of the data set
- Each of these dimensions are defined by a __coordinate__ (1D) array
- It has 2 __Data variables__: `precipitation` and `temperature` that both share the same coordinates

Hence, a `Dataset` object stores *multiple* arrays that have shared dimensions (__Note:__ not all dimensions need to be shared).  It is designed as an in-memory representation of the data model from the netCDF file format.

![](http://xarray.pydata.org/en/stable/_images/dataset-diagram.png)

```{code-cell} ipython3
ds["temperature"].shape, ds["temperature"].dims
```

The data and coordinate variables are also contained separately in the `data_vars` and `coords` dictionary-like attributes of a `xarray.DataSet` to access them directly:

- The data variables:

```{code-cell} ipython3
ds.data_vars
```

- The data coordinates:

```{code-cell} ipython3
ds.coords
```

If you rather use an alternative name for a given variable, use the `rename` method:

```{code-cell} ipython3
ds.rename({"precipitation": "rain"})
```

__Note:__ _the renaming is not entirely correct as rain is just a part of all precipitation (see https://en.wikipedia.org/wiki/Precipitation)._

+++

Adding new variables to the data set is very similar to Pandas/GeoPandas:

```{code-cell} ipython3
ds["precipitation_m"] = ds["precipitation"]/1000.
```

```{code-cell} ipython3
ds
```

### Selecting `DataSet` data

+++

Each of the data variables can be accessed as a single `xarray.DataArray` similar to selecting dictionaries or DataFrames:

```{code-cell} ipython3
type(ds["precipitation"]), type(ds["temperature"])
```

One can select multiple variables at the same time as well by passing a list of variable names:

```{code-cell} ipython3
ds[["temperature", "precipitation"]]
```

Or the other way around, use the `drop_vars` to drop variables from the data set:

```{code-cell} ipython3
ds.drop_vars("temperature")
```

<div class="alert alert-info" style="font-size:120%">

**NOTE**: <br>

Selecting a single variable using `[]` results into a `xarray.DataArray`, selecting multiple variables using a list `[[..., ...]]` results into a `xarray.DataSet`. Using `drop_vars` always returns a `xarray.DataSet`.

</div>

+++

The selection with `sel` works as well with `xarray.DataSet`, selecting the data _for all variables in the DataSet_ and returning a DataSet:

```{code-cell} ipython3
ds.sel(year=2016)
```

The inverse of the `sel` method is the `drop_sel` which returns a DataSet with the enlisted indices removed:

```{code-cell} ipython3
ds.drop_sel(year=[2016])
```

### DataSet plotting

+++

Plotting for data set level is rather limited. A typical use case that is supported to compare two data variables are scatter plots:

```{code-cell} ipython3
ds.plot.scatter("temperature", "precipitation", s=1, alpha=0.1)
```

```{code-cell} ipython3
ds.plot.scatter("temperature", "precipitation", s=1, alpha=0.1, col="year")  # try also hue instead of col; requires hue_style="discrete"
```

### DataSet reductions

+++

Datasets support arithmetic operations by automatically looping over all data variables and supports most of the same methods found on `xarray.DataArray`:

```{code-cell} ipython3
ds.mean()
```

```{code-cell} ipython3
ds.max(dim=["x", "y"])
```

__Note__ Using the names of the data variables (which is actually element-wise operations with DataArrays) makes a calculation very self-describing, e.g.

```{code-cell} ipython3
(ds["temperature"] * ds["precipitation"]).sel(year=2016).plot.imshow()
```

### Let's practice

+++

For the next set of exercises, we introduce the [ERA5-Land monthly averaged data](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land-monthly-means?tab=overview). 

> ERA5-Land is a reanalysis dataset providing a consistent view of the evolution of land variables over several decades. Reanalysis combines model data with observations from across the world into a globally complete and consistent dataset using the laws of physics. 

For these exercises, a subset of the data set focusing on Belgium has been prepared, containing the following variables:

- `sf`: Snowfall (_m of water equivalent_)
- `sp`: Surface pressure (_Pa_)
- `t2m`: 2 metre temperature (_K_)
- `tp`: Total precipitation (_m_)
- `u10`: 10 metre U wind component (_m/s_)

The dimensions are the `longitude`, `latitude` and `time`, which are each represented by a corresponding coordinate.

```{code-cell} ipython3
era5 = xr.open_dataset("./data/era5-land-monthly-means_example.nc")
era5
```

<div class="alert alert-success">

**EXERCISE**:

The [short names used by ECMWF](https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation) are not very convenient to understand. Rename the variables of the  data set according to the following mapping:
    
- `sf`: snowfall_m
- `sp`: pressure_pa
- `t2m`: temperature_k
- `tp`: precipitation_m
- `u10`: wind_ms   
    
Save the result of the mapping as the variable `era5_renamed`.

<details><summary>Hints</summary>

* Both `rename` and `rename_vars` can be used to rename the DataSet variables
* The `rename` function requires a `dict-like` input with the current names as the keys and the new names as the values. 

</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

mapping = {
    "sf": "snowfall_m",
    "sp": "pressure_pa",
    "t2m": "temperature_k",
    "tp": "precipitation_m",
    "u10": "wind_ms"
}

era5_renamed = era5.rename(mapping)
era5_renamed
```

__Note:__ _Make sure you have the variable `era5_renamed` correctly loaded for the following exercises. If not, load the solution of the previous exercise._

+++

<div class="alert alert-success">

**EXERCISE**:

Start from the `era5_renamed` variable. You are used to work with temperatures defined in degrees celsius instead of Kelvin. Add a new data variable to `era5_renamed`, named `temperature_c`, by converting the `temperature_k` into degrees celsius:
    
$T_{^{\circ}C} = T_{K} - 273.15$
    
Create a histogram of the `temperature_c` to check the distribution of all the temperature valus in the data set. Use an appropriate number of bins to draw the histogram.

<details><summary>Hints</summary>

* Xarray - similar to Numpy - applies the mathematical operation element-wise, so no need for loops.
* Most plot functions work on `DataArray`, so make sure to select the variable to apply the `.plot.hist()`.
* One can define the number of bins using the `bins` parameter in the `hist` method.

</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

era5_renamed["temperature_c"] = era5_renamed["temperature_k"] - 273.15
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

era5_renamed["temperature_c"].plot.hist(bins=50);
```

<div class="alert alert-success">

**EXERCISE**:

Calculate the total snowfall of the entire region of the dataset in function of time and create a line plot showing total snowfall in the y-axis and time in the x-axis.

<details><summary>Hints</summary>

* You need to calculate the total (`sum`) snowfall (`snowfall_m`) in function of time, i.e. aggregate over both the `longitude` and `latitude` dimensions (`dim=["latitude", "longitude"]`).
* As the result is a DataArray with a single dimension, the default `plot` will show a line, but you can be more explicit by saying `.plot.line()`.

</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

era5_renamed["snowfall_m"].sum(dim=["latitude", "longitude"]).plot.line(figsize=(18, 5))
```

<div class="alert alert-success">

**EXERCISE**:

The speed to sound is temperature linearly dependent:
    
$v = 331.5 + (0.6 \cdot T)$
    
with $v$ the speed of light and $T$ the temperature in degrees celsius.    
    
Add a new variable to the `era5_renamed` data set, called `speed_of_light_m_s`, that calculates for each location and each time stamp in the data set the temperature corrected speed of light.
    
Create a scatter plot to check the (linear) relationship you just calculated by comparing all the `speed_of_light_m_s` and `temperature_c` data points in the data set.

<details><summary>Hints</summary>

* Creating a new variable is similar to GeoPandas/Pandas/dictionaries, `ds["MY_NEW_VAR"] = ...`.
* Remember, calculations are __element-wise__ just as in Numpy/Pandas; so no need for loops. The numbers (331.5, 0.6) are broadcasted to all elements in the data set to do the calculation.
* To compare two variables in a data set visually, `plot.scatter()` it is.

</details>    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

era5_renamed["speed_of_light_m_s"] = 331.5 + (0.6*era5_renamed["temperature_c"])
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

era5_renamed.plot.scatter("temperature_c", "speed_of_light_m_s", s=1, alpha=0.1)
```

```{code-cell} ipython3

```

```{code-cell} ipython3

```

------- TODO ------

```{code-cell} ipython3

```

```{code-cell} ipython3

```

```{code-cell} ipython3

```

```{code-cell} ipython3

```

## Working with time series

```{code-cell} ipython3
era5 = xr.open_dataset("./data/era5-land-monthly-means.nc")
mapping = {
    "sf": "snowfall_m",
    "sp": "pressure_pa",
    "t2m": "temperature_k",
    "tp": "precipitation_m",
    "u10": "wind_ms"
}
era5_renamed = era5.rename(mapping)
era5_renamed
```

### groupby

+++

If we are interested in the _average over time_ for each of the levels, we can use a reducton function to get the averages of each of the variables at the same time:

```{code-cell} ipython3
era5_renamed.mean(dim=["time"])
```

But if we wanted the _average for each month of the year_ per level, we would first have to __split__ the data set in a group for each month of the year, __apply__ the average function on each of the months and __combine__ the data again. 

We already learned about the [split-apply-combine](https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html) approach when using Pandas. The syntax of Xarray’s groupby is almost identical to Pandas!

+++

First, extract the month of the year (1-> 12) from each of the date coordinates:

```{code-cell} ipython3
era5_renamed["time"].dt.month  # The coordinates is a Pandas datetime index
```

We can use these arrays in a groupby operation:

```{code-cell} ipython3
era5_renamed.groupby(era["time"].dt.month)
```

Xarray also offers a more concise syntax when the variable you're grouping on is already present in the dataset. This is identical to the previous line:

```{code-cell} ipython3
era5_renamed.groupby("time.month")
```

Next, we apply an aggregation function _for each of the months_ over the `date` dimension in order to end up with: _for each month of the year, the average (over time) for each of the levels_:

```{code-cell} ipython3
era5_renamed.groupby("time.month").mean(dim="time")
```

### resample/rolling

+++

Another (alike) operation - specifically for time series data - is to `resample` the data to another time-aggregation. For example, resample to monthly (`1M`) or yearly (`1Y`) median values:

```{code-cell} ipython3
era5_renamed.resample(time="Y").median()  # 1Y
```

```{code-cell} ipython3
era5_renamed["temperature_k"].sel(latitude=51., longitude=4., method="nearest").plot.line(x="time");
era5_renamed["temperature_k"].sel(latitude=51., longitude=4., method="nearest").resample(time="10Y").median().plot.line(x="time");
```

A similar, but different functionality is `rolling` to calculate rolling window aggregates:

```{code-cell} ipython3
era5_renamed.rolling(time=12, center=True).median()
```

```{code-cell} ipython3
# TODO - convert to new era data set
argo["salinity"].sel(date='2012-10-31').plot.line(y="level", yincrease=False, color="grey");
argo["salinity"].sel(date='2012-10-31').rolling(level=10, center=True).median().plot.line(y="level", yincrease=False, linewidth=3, color="crimson");
plt.legend(), plt.title("");
```

<div class="alert alert-info" style="font-size:120%">

**REMEMBER**: <br>

The [xarray `groupby`](http://xarray.pydata.org/en/stable/groupby.html) with the same syntax as Pandas implements the __split-apply-combine__ strategy. Also [`resample`](http://xarray.pydata.org/en/stable/time-series.html#resampling-and-grouped-operations) and [`rolling`](http://xarray.pydata.org/en/stable/computation.html?highlight=rolling#rolling-window-operations) are available in xarray.
    
__Note:__ Xarray adds a [`groupby_bins`](http://xarray.pydata.org/en/stable/generated/xarray.Dataset.groupby_bins.html#xarray.Dataset.groupby_bins) convenience function for binned groups (instead of each value).

</div>

+++

### Let's practice

+++

<div class="alert alert-success">

**EXERCISE**:
    
Create the yearly total snowfall from 1991 up to 2005 and convert the snowfall into cm.  Make a plot (`imshow`) with each of the individual years in a separate subplot divided into 3 rows and 5 columns.
    
Make sure to update the name of the snowfall variable and/or colorbar label to make sure it defines the unit in cm.
 

<details><summary>Hints</summary>

* When selecting time series data from a coordinate with datetime-aware data, one can use strings to define a date. In combination with `slice`, the selection of the required years becomes `slice("1991", "2005")`.
* From montly to yearly data is a `resample` of the data.
* Use `.rename(NEW_NAME)` to update the name of a `DataArray`
* xarray supports _facetting_ directly, check out the `col` and `col_wrap` parameters in the plot functions of xarray or check http://xarray.pydata.org/en/stable/user-guide/plotting.html#faceting.
* To update the colorbar unit use, the `cbar_kwargs` option.

</details>    
    
</div>

```{code-cell} ipython3
snowfall_1991_2005 = era5_renamed.sel(time=slice("1991", "2005"))["snowfall_m"]
snowfall_yearly = snowfall_1991_2005.resample(time="Y").sum()*100
snowfall_yearly = snowfall_yearly.rename("snowfall_cm")
snowfall_yearly.plot.imshow(col="time", col_wrap=5, cmap=cmocean.cm.ice, 
                            cbar_kwargs={"label": "snowfall (cm)"})
```

```{code-cell} ipython3

```

```{code-cell} ipython3

```

---------------

__Note:__ Values are only read from disk when needed. For example, the following statement only reads the coordinate information and the metadata. The data itself is not yet loaded:

```{code-cell} ipython3
data_file = "./data/gent/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff"
```

```{code-cell} ipython3
gent = xr.open_rasterio(data_file)
gent
```

`load()` will explicitly load the data into memory:

```{code-cell} ipython3
xr.open_rasterio(data_file).load()
```

```{code-cell} ipython3

```

## From DataSet to DataArray and back

+++

Conversion from and to __TODO__

```{code-cell} ipython3
xr_array = xr_array.assign_coords(band=("band", ["b4", "b8"]))
xr_data = xr_array.to_dataset(dim="band")
xr_data
```

Why do we want to use a Dataset instead of DataArray?

* We can actually have multiple arrays that are logically different variables, eg temperature and pressure with the same (lon, lat, time) dimensions
* For some cases it can be more convenient to work with

+++

Recap the NDVI exercise of the previous notebook, using a stacked version of the 4th and 8th Sentinel band:

```{code-cell} ipython3
xr_array = xr.open_rasterio("./data/gent/raster/2020-09-17_Sentinel_2_L1C_B0408.tiff")
xr_array
```

In Numpy, we would do:

```{code-cell} ipython3
b48_bands = xr_array.values  # 0 is band 4 and 1 is band 8
b48_bands.shape
```

```{code-cell} ipython3
ndvi_np = (b48_bands[1] - b48_bands[0])/(b48_bands[0] + b48_bands[1]) # or was it b48_bands[0] -  b48_bands[1] ?
```

```{code-cell} ipython3
plt.imshow(ndvi_np, cmap="YlGn")
```

In __xarray__:

```{code-cell} ipython3
xr_array = xr_array.assign_coords(band=("band", ["b4", "b8"]))
xr_data = xr_array.to_dataset(dim="band")
```

```{code-cell} ipython3
ndvi_xr = (xr_data["b8"] - xr_data["b4"])/(xr_data["b8"] + xr_data["b4"])
```

```{code-cell} ipython3
plt.imshow(ndvi_xr, cmap="YlGn")
```

The result is the same, but no more struggling on what index is representing which variable!

```{code-cell} ipython3
np.allclose(ndvi_xr.data, ndvi_np)
```

We can keep the result together with the other data variables by adding a new variable to the data, in a very similar way as we created a new column in Pandas:

```{code-cell} ipython3
xr_data["ndvi"] = ndvi_xr
xr_data
```

```{code-cell} ipython3

```
