---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.12.0
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

<p><font size="6"><b>Numpy</b></font></p>


> *DS Python for GIS and Geoscience*  
> *October, 2020*
>
> *© 2020, Joris Van den Bossche and Stijn Van Hoey. Licensed under [CC BY 4.0 Creative Commons](http://creativecommons.org/licenses/by/4.0/)*

---

```{code-cell} ipython3
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D

import rasterio
from rasterio.plot import plotting_extent, show
```

## Introduction

+++

On of the most fundamental parts of the scientific python 'ecosystem' is [numpy](https://numpy.org/). A lot of other packages - you already used Pandas and GeoPandas in this course - are built on top of Numpy and the `ndarray`  (n-dimensional array) data type it provides. 

```{code-cell} ipython3
import numpy as np
```

Let's start again from reading in a GeoTiff data set from file, thiss time a Sentinal Band 4 of the City of Ghent:

```{code-cell} ipython3
with rasterio.open("./data/gent/raster/2020-09-17_Sentinel_2_L1C_B04.tiff") as src:
    b4_data = src.read()
    b4_data_meta = src.meta
    show(src)
```

As we learnt in the previous lesson, Rasterio returns a Numpy `ndarray`:

```{code-cell} ipython3
type(b4_data)
```

```{code-cell} ipython3
b4_data
```

Numpy supports different `dtype`s (`float`, `int`,...), but all elements of an array do have the same dtype. Note that NumPy auto-detects the data-type from the input.

```{code-cell} ipython3
b4_data.dtype
```

The data type of this specific array `b4_data` is 16bit unsigned integer. More information on the data types Numpy supports is available in the [documentation](https://numpy.org/devdocs/user/basics.types.html#array-types-and-conversions-between-types). Detailed info on data types is out of scope of this course, but remember that using 16bit unsigned integer, it can contain `2**16` different (all positive) integer values:

```{code-cell} ipython3
2**16
```

Let's check this by calculating the minimum and maximum value in the array:

```{code-cell} ipython3
b4_data.min(), b4_data.max()
```

Converting to another data type is supported by `astype` method. When floats are preferred during calculation:

```{code-cell} ipython3
b4_data.astype(float)
```

```{code-cell} ipython3
b4_data.max()
```

Just as any other object in Python, the `ndarray` has a number of attributes. We already checkes the `dtype` attribute. The `shape` and `ndim` of the array are other relevant attribute:

```{code-cell} ipython3
b4_data.shape, b4_data.ndim
```

Hence, we have a single band with dimensions (317, 625) and data type `uint16`. Compare this to the metadata stored in the geotiff file:

```{code-cell} ipython3
#!gdalinfo ./data/gent/raster/2020-09-17_Sentinel_2_L1C_B04.tiff
```

The metadata on the dimensions and the datatype correspond, but the spatial information is lost when we only store the Numpy array.

+++

Numpy works very well together with the other fundamental scientific Python package [Matplotlib](https://matplotlib.org/). An useful plot function to know when working with raster data is `imshow`:

```{code-cell} ipython3
fig, ax = plt.subplots()
ax.imshow(b4_data.squeeze());
```

__Note:__ Numpy function `squeeze` used to get rid of the single-value dimension of the numpy array.

+++

As the Numpy array does not contain any spatial information, the x and y axis labels are defined by the indices of the array. Remark that the Rasterio plot returned this plot with the coordinate information in the axis labels. 

With a small trick, the same result can be achieved with Matplotlib:

1. When reading in a data set using Rasterio, use the `plotting_extent` function from rasterio to get the spatial extent:

```{code-cell} ipython3
from rasterio.plot import plotting_extent

with rasterio.open("./data/gent/raster/2020-09-17_Sentinel_2_L1C_B04.tiff") as src:
    b4_data = src.read()
    b4_data_meta = src.meta
    b4_data_extent = plotting_extent(src)  # NEW
```

```{code-cell} ipython3
b4_data_extent
```

2. Add the `extent` argument to the `imshow` plot

```{code-cell} ipython3
fig, ax = plt.subplots()
ax.imshow(b4_data.squeeze(), extent=b4_data_extent)
```

<div class="alert alert-info" style="font-size:120%">

**REMEMBER**: <br>

The [`numpy` package](https://numpy.org/) is the backbone of the scientific Python ecosystem. The `ndarray` provides an efficient data type to store and manipulate raster data, but it does NOT contain any spatial information.
    
Use the spatial `extent` trick to add coordinate information to imshow plot axis. Convert to the preferred datatype using `astype()` method.

</div>

+++

## Reshape, slice and index

```{code-cell} ipython3
b4_data.shape
```

We already used `squeeze` to remove the single-value dimension. We could also select the data we needed, similar to slicing in lists or Pandas DataFrames:

```{code-cell} ipython3
b4_data[0]
```

```{code-cell} ipython3
b4 = b4_data[0]
b4.shape
```

If you do not like the order of dimensions of the data, you can switch these using `transpose`:

```{code-cell} ipython3
b4.transpose(1, 0).shape
```

Getting rid of the dimensions and flattening all values into a single 1-D array can be done using `flatten` method:

```{code-cell} ipython3
b4.flatten().shape
```

Flattening an arrya is useful to create a histogram with Matplotlib:

```{code-cell} ipython3
plt.hist(b4.flatten(), bins=100);
```

```{code-cell} ipython3
# slice, subsample, reverse
# slice + assign
# fancy indexing
# fancy indexing + assign
```

```{code-cell} ipython3
b4 = b4_data[0]
```

Select a specific row/column:

```{code-cell} ipython3
b4[10].shape
```

```{code-cell} ipython3
b4[:, -2:].shape
```

Select every nth element in a given dimension:

```{code-cell} ipython3
b4[100:200:10, :].shape
```

Reversing an array:

```{code-cell} ipython3
b4[:, ::-1].shape  # Note you can also np.flip an array
```

```{code-cell} ipython3
b4[0, :4]
```

```{code-cell} ipython3
b4_rev = b4[:, ::-1]
b4_rev[0, -4:]
```

You can also combine assignment and slicing:

```{code-cell} ipython3
b4[0, :3] = 10
b4
```

Use a __condition__ to select data, also called fancy indexing or boolean indexing:

```{code-cell} ipython3
b4 < 1000
```

Onle keep the data which are True for the given condition

```{code-cell} ipython3
b4[b4 < 1000]
```

Or combine assignment and fancy indexing, e.g. a reclassification of the raster data:

```{code-cell} ipython3
b4[b4 < 5000] = 0  # assign the value 0 to all elements with a value lower than 5000
```

```{code-cell} ipython3
b4
```

A powerfull shortcut to handle this kind or reclassifications is the `np.where` function:

```{code-cell} ipython3
np.where(b4 < 5000, 10, b4)
```

<div class="alert alert-success">

**EXERCISE**:

* Read in the file `./data/gent/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff` with rasterio and assign the data to a new variable `tc_data`.  
* Select only the *second* layer of `tc_data` and assign the output to a new variable `tc_g`.
* Assign to each of the elements in the `tc_g` array with a value above 15000 the new value 65535.
    
<details><summary>Hints</summary>

* You can combine the assignment of new values together with fancy indexing of a numpy array.
* Python (and also Numpy) uses 0 as the first-element index

</details>
    
</div>

```{code-cell} ipython3
:clear_cell: true

with rasterio.open("./data/gent/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff") as src:
    tc_data = src.read()
```

```{code-cell} ipython3
:clear_cell: true

# Get the green channel
tc_g = tc_data[1]
```

```{code-cell} ipython3
:clear_cell: true

# Convert all values above 15000
tc_g[tc_g > 15000] = 65535
tc_g
```

<div class="alert alert-success">

**EXERCISE**:

Subsample the ndarray `tc_data` by taking only the one out of each 5 data points for all layers at the same time (Be aware that this is a naive resampling implementation for educational purposes only). 
    
<details><summary>Hints</summary>

* The result should still be a 3-D array with 3 elements in the first dimension.

</details>   
    
</div>

```{code-cell} ipython3
:clear_cell: true

with rasterio.open("./data/gent/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff") as src:
    tc_data = src.read()
```

```{code-cell} ipython3
:clear_cell: true

# subsample the data
tc_data[:, ::5, ::5].shape
```

<div class="alert alert-success">

**EXERCISE**:

Elements with the value `65535` do represent 'Not a Number' (NaN) values. However, Numpy does not support NaN values for integer data, so we'll convert to float first as data type. After reading in the data set `./data/gent/raster/2020-09-17_Sentinel_2_L1C_B04_(Raw).tiff` (assign data to variable `b4_data`):
    
* Count the number of elements that are equal to `65535`
* Convert the data type to `float`, assign the result to  a new variable `b4_data_f`
* Assign Nan (`np.nan`) value to each of the elements of `b4_data_f` equal to `65535`
* Count the number of Nan values in the `b4_data_f` data
* Make a histogram of both the `b4_data` and `b4_data_f` data. Can you spot the difference?
    
    
<details><summary>Hints</summary>

* `np.nan` represents _Not a Number (NaN)_ in Numpy. You can assign an element to it, e.g. `dummy[2] = np.nan`
* `np.sum` will by default sum all of the elements of the input array and can also count boolean values (True = 1 and False = 0), resulting from a conditional expression. 
* To test if a value is a nan, Numpy provides `np.isnan(...)` which results in an element-wise check returning boolean values.
* Check the help of the `plt.hist` command to find out more about the `bins` and the `log` arguments.

</details>    
    
   
</div>

```{code-cell} ipython3
:clear_cell: true

with rasterio.open("./data/gent/raster/2020-09-17_Sentinel_2_L1C_B04.tiff") as src:
    b4_data = src.read()
```

```{code-cell} ipython3
:clear_cell: true

# Count the number of cells with value 65535
np.sum(b4_data == 65535)
```

```{code-cell} ipython3
:clear_cell: true

# Convert to float and make 65535 equal to Nan
b4_data_f = b4_data.astype(float)
b4_data_f[b4_data == 65535] = np.nan
```

```{code-cell} ipython3
:clear_cell: true

# Count the number of cells with value 0
np.sum(np.isnan(b4_data_f))
```

```{code-cell} ipython3
:clear_cell: true

# Create the histogram plots
fig, (ax0, ax1) = plt.subplots(1, 2, sharey=True)
ax0.hist(b4_data.flatten(), bins=30, log=True);
ax1.hist(b4_data_f.flatten(), bins=30, log=True);
```

## Reductions, element-wise calculations and broadcasting

+++

Up until now, we worked with the 16bit integer values. For specific applications we might want to rescale this data. A (fake) example is the linear transformation to the range 0-1 after log conversion of the data. To do so, we need to calculate _for each element_ in the original $b$ array the following:

+++

$$x_i= \log(b_i)$$
$$z_i=\frac{x_i-\min(x)}{\max(x)-\min(x)}$$

+++

__1. reductions__

As part of it, we need the minimum `min(x)` and the maximum `max(x)` of the array. These __reductions__ (aggregations) are provided by Numpy and can be applied along one or more of the data dimensions, called the __axis__:

```{code-cell} ipython3
dummy = np.arange(1, 10).reshape(3, 3)
dummy
```

```{code-cell} ipython3
np.min(dummy), np.min(dummy, axis=0), np.min(dummy, axis=1)
```

```{code-cell} ipython3
dummy = np.arange(1, 25).reshape(2, 3, 4)
dummy.shape, dummy
```

```{code-cell} ipython3
np.min(dummy), np.min(dummy, axis=0), np.min(dummy, axis=(0, 1)), np.min(dummy, axis=(0, 2))
```

In some applications, the usage of the `keepdims=True` is useful to keep the number of dimensions after reduction:

```{code-cell} ipython3
np.min(dummy, axis=(0, 2), keepdims=True)
```

When working with Nan values, the result will be Nan as well:

```{code-cell} ipython3
np.min(np.array([1., 2., np.nan]))
```

Use the `nanmin`, `nan...` version of the function instead, if available:

```{code-cell} ipython3
np.nanmin(np.array([1., 2., np.nan]))
```

__2. Element-wise__

+++

The __for each element__ is crucial for Numpy. The typical answer in programming would be a `for`-loop, but Numpy is optimized to do these calculations __element-wise__ (i.e. for all elements together):

```{code-cell} ipython3
dummy = np.arange(1, 10)
dummy
```

```{code-cell} ipython3
dummy*10
```

Instead of:

```{code-cell} ipython3
[el*20 for el in dummy]
```

Numpy provides most of the familiar arithmetic operators to apply on an element-by-element basis:

```{code-cell} ipython3
np.exp(dummy), np.sin(dummy), dummy**2, np.log(dummy)
```

For some function, you can either use the `np.min(my_array)` or the `my_array.min()` approach:

```{code-cell} ipython3
dummy.min() == np.min(dummy)
```

__3. Broadcasting__

+++

When we combine arrays with different shapes during arithmetic operations, Numpy applies a set of __broadcoasting__ rules and the smaller array is _broadcast_ across the larger array so that they have compatible shapes. An important consequence for out application is:

```{code-cell} ipython3
np.array([1, 2, 3]) + 4. , np.array([1, 2, 3]) + np.array([4.]), np.array([1, 2, 3]) + np.array([4., 4., 4.])
```

The smallest array is broadcasted to make both compatible. It starts with the trailing (i.e. rightmost) dimensions. Exploring all the rules are out of scope in this lesson and are well explained in the [broadcasting Numpy documentation](https://numpy.org/devdocs/user/basics.broadcasting.html#general-broadcasting-rules). 

+++

__Back to our function__

+++

By combining these three elements, we know enough to translate our conversion into Numpy code on the example data set:

```{code-cell} ipython3
with rasterio.open("./data/gent/raster/2020-09-17_Sentinel_2_L1C_B04.tiff") as src:
    b4_data = src.read()
b4_data = b4_data.squeeze().astype(float)    # squeeze and convert to float
b4_data[b4_data == 0.0] = 0.00001  # to overcome zero-division error
```

Take the log of al the values __element-wise__:

```{code-cell} ipython3
b4_data_log = np.log(b4_data)
```

Get the min and max __reductions__:

```{code-cell} ipython3
b4_min, b4_max = b4_data_log.min(), b4_data_log.max()
```

__Broadcast__ our single value `b4_min` and `b4_max` to all elements of `b4_data_log`:

```{code-cell} ipython3
b4_rescaled = ((b4_data_log - b4_min)/(b4_max - b4_min))
```

```{code-cell} ipython3
plt.hist(b4_rescaled.flatten(), bins=100);
```

__Remark 1:__ One-dimensional linear interpolation towards a new value range can be calculated using the `np.interp` function as well. For the range 0 -> 1: 

```
np.interp(b4_data, (b4_data.min(), b4_data.max()), (0, 1))
```

+++

__Remark 2: Why not iterate over the values of a list?__

+++

Let's use the  rescaling example to compare the calculation with Numpy versus a list comprehension (for-loop in Python):

```{code-cell} ipython3
b4_min, b4_max = b4_data.min(), b4_data.max()
```

With Numpy:

```{code-cell} ipython3
%%time
rescaled_values_1 = ((b4_data - b4_min)/(b4_max - b4_min))
```

Using a list with a for loop:

```{code-cell} ipython3
b4_as_list = b4_data.flatten().tolist()
```

```{code-cell} ipython3
%%time
rescaled_values_2 = [((data_point - b4_min)/(b4_max - b4_min)) for data_point in b4_as_list]
```

```{code-cell} ipython3
np.allclose(rescaled_values_1.flatten(), rescaled_values_2)  # np.allclose also works element wise
```

<div class="alert alert-info" style="font-size:120%">

**REMEMBER**: <br>

The combination of element-wise calculations, efficient reductions and broadcasting provides Numpy a lot of power. In general, it is a good advice to __avoid for loops__ when working with Numpy arrays.

</div>

+++

### Let's practice!

+++

<div class="alert alert-success">

**EXERCISE**:

The data set `./data/herstappe/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff` (assign to variable `herstappe_data`) contains 3 bands. The `imshow` function of Matplotlib can plot 3-D (RGB) data sets, but when running `plt.imshow(herstappe_data)`, we got the following error:
    
    ```
    ...
    TypeError: Invalid shape (3, 227, 447) for image data
    ```

- Check in the help op `plt.imshow` why the `herstappe_data` can not be plot as such
- Adjust the data to fix the behavior of `plt.imshow(herstappe_data)`
    
Next, plot a greyscale version of the data as well. Instead of using a custom function just rely on the sum of the 3 bands as a proxy.
    
<details><summary>Hints</summary>

* In a Jupyter Notebook, us the SHIFT-TAB combination when the cursor is on the `imshow` function or type in a new cell `?plt.imshow` to see the documentation of a function.
* The `imshow` function requires the different color bands as last dimension, so we will need to transpose the image array.
* Add the extent to see the coordinates in the axis labels.
* A greyscale image requires a greyscale `cmap`, checkt he available names in [the documentation online](https://matplotlib.org/tutorials/colors/colormaps.html)

</details>    
    
</div>

```{code-cell} ipython3
:clear_cell: true

with rasterio.open("./data/herstappe/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff") as src:
    herstappe_data = src.read()
    herstappe_extent = plotting_extent(src)
```

```{code-cell} ipython3
:clear_cell: true

# Make a RGB plot
fig, ax = plt.subplots(figsize=(12, 5))
plt.imshow(herstappe_data.transpose(1, 2, 0), extent=herstappe_extent);
```

```{code-cell} ipython3
:clear_cell: true

# Make a Grey scale plot
greyscale_data = herstappe_data.sum(axis=0)
fig, ax = plt.subplots(figsize=(12, 5))
plt.imshow(greyscale_data, extent=herstappe_extent, cmap="Greys");
```

<div class="alert alert-success">

**EXERCISE**:

The data set `./data/herstappe/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff` (assign to variable `herstappe_data`) has values ranging in between 0.11325, 0.8575. To improve the quality of the visualization, stretch __each of the layers individually__ to the values to the range 0. to 1. with a linear transformation: 
    
$$z_i=\frac{x_i-\min(x)}{\max(x)-\min(x)}$$

Make a plot of the end result and compare with the plots of the previous exercise. 
   
<details><summary>Hints</summary>

* Keep into account that the data set is 3-dimensional. Have a look at the optional arguments for the reduction/aggregation functions in terms of `axis` and `keepdims`. 
* You need the minimal/maximal value over 2 axis to end up with a min/max for each of the layers.
* Broadcasting starts comparison of the alignment on the last dimension.

</details>    
    
</div>

```{code-cell} ipython3
:clear_cell: false

with rasterio.open("./data/herstappe/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff") as src:
    herstappe_data = src.read()
    herstappe_extent = plotting_extent(src)
```

```{code-cell} ipython3
:clear_cell: true

# Calculate the min and max for each channel
h_min = herstappe_data.min(axis=(1, 2), keepdims=True)
h_max = herstappe_data.max(axis=(1, 2), keepdims=True)
```

```{code-cell} ipython3
:clear_cell: true

# Rescale the data
herstappe_rescaled = ((herstappe_data - h_min)/(h_max - h_min))
```

```{code-cell} ipython3
:clear_cell: true

# Make a plot
fig, ax = plt.subplots(figsize=(12, 5))
plt.imshow(herstappe_rescaled.transpose(1, 2, 0), extent=herstappe_extent);
```

<div class="alert alert-success">

**EXERCISE**:
    
You want to reclassify the values of the 4th band data to a fixed set of classes:
    
* x < 0.05 need to be 10
* 0.05 < x < 0.1 need to be 20
* x > 0.1 need to be 30
       
Use the data set `./data/gent/raster/2020-09-17_Sentinel_2_L1C_B04_(Raw).tiff` (assign data to variable `b4_data`):
    
* Read the data set and exclude the single-value dimension to end up with a 2D array. 
* Convert to float data type. and normalize the values to the range [0., 1.].
* Create a new variable `b4_data_classified` with the same shape as `b4_data` but datatype int.
* Assign the new values (10, 20, 30) to the elements for which each of the conditions apply. 
* Make a image plot of the reclassified variable `b4_data_classified`.
    
</div>

```{code-cell} ipython3
:clear_cell: false

with rasterio.open("./data/gent/raster/2020-09-17_Sentinel_2_L1C_B04.tiff") as src:
    b4_data = src.read()
    b4_data_extent = plotting_extent(src)
```

```{code-cell} ipython3
:clear_cell: true

# Squeeze to 2D float array 
b4_data = b4_data.squeeze().astype(float)
```

```{code-cell} ipython3
:clear_cell: true

# Rescale the data
b4_data = (b4_data - b4_data.min())/(b4_data.max() - b4_data.min())
```

```{code-cell} ipython3
:clear_cell: true

# Create a new array with the same shape as the original b4_data
b4_data_classified = np.empty_like(b4_data).astype(int)
```

```{code-cell} ipython3
:clear_cell: true

# Assign the new values according to the classes
b4_data_classified[b4_data < 0.05] = 10
b4_data_classified[(0.05 <= b4_data) & (b4_data < 0.1)] = 20
b4_data_classified[0.1 <= b4_data] = 30
```

```{code-cell} ipython3
:clear_cell: true

# Create an image plot
fig, ax = plt.subplots(figsize=(12, 5))
img = ax.imshow(b4_data_classified, extent=b4_data_extent)
fig.colorbar(img, values=[10, 20, 30], ticks=[10, 20, 30])
```

<div class="alert alert-success">

**EXERCISE**:

The data sets `./data/gent/raster/2020-09-17_Sentinel_2_L1C_B04.tiff` and `./data/gent/raster/2020-09-17_Sentinel_2_L1C_B08.tiff` contain respectively the 4th and the 8th band of a sentinel satellite image. To derive the [Normalized Difference Vegetation Index) (NDVI)](https://nl.wikipedia.org/wiki/Normalized_Difference_Vegetation_Index), the two bands need to be combined as follows:
    
$$\frac{band_8 - band_4}{band_8 + band_4} $$
    
Process the images and create a plot of the NDVI:
    
- Read both data sets using Rasterio and store them in resp. `b4_data` and `b8_data`. 
- Combine both data sets using the `np.vstack` function and assign it to the variable `b48_bands`
- Transform the data range of each of the layers to the range .0 - 1.
- For the values equal to zero in the `b48_bands` data set, assign a new (very small) value 1e-6
- Calculate the NDVI
- Plot the NDVI and select an appropriate colormap.
    
<details><summary>Hints</summary>

* For more specific adjustments to the colormap, have a check on the [Matplotlib documentation on colormap normalization](https://matplotlib.org/3.3.2/tutorials/colors/colormapnorms.html)

</details>   
           
</div>

```{code-cell} ipython3
:clear_cell: true

with rasterio.open("./data/gent/raster/2020-09-17_Sentinel_2_L1C_B04.tiff") as src:
    b4_data = src.read()
    b4_extent = plotting_extent(src)
with rasterio.open("./data/gent/raster/2020-09-17_Sentinel_2_L1C_B08.tiff") as src:
    b8_data = src.read() 
```

```{code-cell} ipython3
:clear_cell: true

# Combine both arrays by stacking them together
b48_bands = np.vstack((b4_data, b8_data))  # 0 is b4 and 1 is b8
```

```{code-cell} ipython3
b48_bands.shape
```

```{code-cell} ipython3
:clear_cell: true

# Rescale the data to 0-1
b48_min = b48_bands.min(axis=(1, 2), keepdims=True)
b48_max = b48_bands.max(axis=(1, 2), keepdims=True)
b48_bands = ((b48_bands - b48_min)/(b48_max - b48_min))
```

```{code-cell} ipython3
:clear_cell: true

# Assign very small value to 0-values
b48_bands[b48_bands == 0] = 1e-6
```

```{code-cell} ipython3
:clear_cell: true

# Calculate the ndvi using the stacked data
ndvi = (b48_bands[1] - b48_bands[0])/(b48_bands[0] + b48_bands[1])
```

+++ {"clear_cell": false}

Using a Matplotlib norm to adjust colormap influence on image https://matplotlib.org/api/_as_gen/matplotlib.colors.TwoSlopeNorm.html

```{code-cell} ipython3
:clear_cell: true

# A Sequential colormap `YlGn` with a normalization on the color limits
import matplotlib.colors as mcolors
div_norm = mcolors.Normalize(0.1, 0.8)
fig, ax = plt.subplots(figsize=(14, 5))
ll = ax.imshow(ndvi, cmap="YlGn", extent=b4_extent, norm=div_norm)
fig.colorbar(ll);
```

```{code-cell} ipython3
:clear_cell: true

# A Diverging colormap `RdYlGn` with a normalization on the color limits in two directions of the central point:
div_norm = mcolors.TwoSlopeNorm(vmin=-0.1, vcenter=0.4, vmax=0.8)
fig, ax = plt.subplots(figsize=(14, 5))
ll = ax.imshow(ndvi, cmap="RdYlGn", extent=b4_extent, norm=div_norm)
fig.colorbar(ll);
plt.axis('off');
```

---

## For the curious: Some more building blocks

+++

Numpy provides lower-level building blocks used by other packages and you will once in a also need to rely on these functions to do some custom implementation. Some other useful building blocks with repect to reclassification could potentially help you:

+++

- Remember the `np.where` function?

```{code-cell} ipython3
dummy = np.arange(1, 10).reshape(3, 3)
dummy
```

```{code-cell} ipython3
np.where(dummy > 4, 0, dummy)
```

- Clip the values in yanour array to defined limits can be done using `np.clip`

```{code-cell} ipython3
dummy = np.arange(1, 10).reshape(3, 3)
dummy
```

```{code-cell} ipython3
np.clip(dummy, 2, 6)
```

- Numpy provides also a `np.histogram` function, which is really useful to get the bincounts over a custom bin-set:

```{code-cell} ipython3
np.histogram(b4_data_classified, bins=[5, 15, 25, 35])
```

```{code-cell} ipython3
np.histogram(b4_data, bins=[0.001, 0.1, 0.2, 0.5])
```

- The `np.digitize` function return the indices of the bins to which each value in input array belongs. As such, it can be used to select and manipulate values containing to a specific bin:

```{code-cell} ipython3
dummy = np.arange(9).reshape(3, 3)
np.random.shuffle(dummy)
dummy
```

Define the bin to which each of the values belong to, using the bins x<2, 2<=x<4, x>=4:

```{code-cell} ipython3
id_mask = np.digitize(dummy, bins=[2, 4])
id_mask
```

```{code-cell} ipython3
dummy[id_mask == 1] = 20
dummy
```

Besides, it is also a practical method to create discrete classified maps:

  1. Apply digitize to create classes:

```{code-cell} ipython3
ndvi_class_bins = [-np.inf, 0, 0.3, np.inf]  # These limits are for demo purposes only 
ndvi_landsat_class = np.digitize(ndvi, ndvi_class_bins)
```

  2. Define custom colors and names:

```{code-cell} ipython3
nbr_colors = ["gray", "yellowgreen", "g"]
ndvi_names = ["No Vegetation", "Bare Area", "Vegetation"]
```

  3. Prepare Matplotlib elements:

```{code-cell} ipython3
nbr_cmap = ListedColormap(nbr_colors)
# fake entries required for each class to create the legend
dummy_data = [Line2D([0], [0], color=color, lw=4) for color in nbr_colors]  
```

  4. Make the plot and add a legend:

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(12, 12))
im = ax.imshow(ndvi_landsat_class, cmap=nbr_cmap, extent=b4_data_extent)
ax.legend(dummy_data, ndvi_names, loc='upper left', framealpha=1)
```

- Find the modal (most common) value in an array is not provided by Numpy itself, but is available in the Scipy package:

```{code-cell} ipython3
from scipy.stats import mode
```

```{code-cell} ipython3
mode(b4_data.flatten()), mode(b4_data_classified.flatten())
```

### Side-note on convolution

+++

In case you need custom convolutions for your 2D array, check the `scipy.signal.convolve` function as the Numpy function only works for 1-D arrays.

```{code-cell} ipython3
from scipy import signal
```

```{code-cell} ipython3
with rasterio.open("./data/gent/raster/2020-09-17_Sentinel_2_L1C_B04.tiff") as src:
    b4_data = src.read()
    b4_data_extent
b4_data = b4_data.squeeze().astype(float)
```

As an example, apply a low pass filter example as window, smoothing the image:

```{code-cell} ipython3
window = np.ones((5, 5), dtype=int)
window[1:-1, 1:-1] = 4
window[2, 2] = 12
window
```

```{code-cell} ipython3
grad = signal.convolve(b4_data, window, mode='same')
```

```{code-cell} ipython3
fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(16, 6))
ax0.imshow(b4_data, extent=b4_data_extent)
ax1.imshow(grad, extent=b4_data_extent)
```

```{code-cell} ipython3

```
