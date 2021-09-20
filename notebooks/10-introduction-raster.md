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

<p><font size="6"><b>Introduction to raster data</b></font></p>


> *DS Python for GIS and Geoscience*  
> *October, 2020*
>
> *© 2020, Joris Van den Bossche and Stijn Van Hoey. Licensed under [CC BY 4.0 Creative Commons](http://creativecommons.org/licenses/by/4.0/)*

---

```{code-cell} ipython3
%matplotlib inline

import numpy as np
import rasterio
from rasterio.plot import show
```

The two primary types of geospatial data are raster and vector data. Vector data structures represent specific features on the Earth’s surface, and assign attributes to those features. 

__Raster data__ is stored as a grid of values which are rendered on a map as pixels. Raster files are different from photographs in that they are spatially referenced. Each pixel represents an area of land on the ground. That area is defined by the spatial resolution of the raster.

+++

![](../img/raster-concept.png)
<small>_Source: Colin Williams, NEON._</small>

+++

## Importing raster data

+++

Similar to geospatial feature based data, rastyer data is often available from specific GIS file formats or data stores, like Geotiff files, Esri grid, NetCDF files, PostGIS (PostgreSQL) database, ...

We can use the [Rasterio library](https://rasterio.readthedocs.io/en/latest/) to read many of those GIS file formats, using the `rasterio.open` function.

Let's start by reading and plotting a Geotiff file (the file is available in the `./data/herstappe/raster` directory):

```{code-cell} ipython3
file_herstappe = "./data/herstappe/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff"
```

```{code-cell} ipython3
with rasterio.open(file_herstappe) as src:
    herstappe = src.read()
    show(herstappe, transform=src.transform)
```

A raster is just an __image__ in local pixel coordinates until we specify what part of the earth the image covers. This is done through the usage of raster file metadata. It depends on the file type how these are stored on disk. When reading in a file, the metadata need to be interpreted as well in order to know the __spatial information__.

+++

## Raster data attributes

+++

To quickly scan the spatial metadata of a Raster data file, let's use the [`gdalinfo` command](https://gdal.org/programs/gdalinfo.html#gdalinfo). 

> The `gdalinfo` command lists information about a raster dataset.

It is not a Python command, but a program that need to be run from the terminal (aka command line). Using a small Jupyter notebook - `!` trick, we can use it within the notebook as well: 

```{code-cell} ipython3
!gdalinfo -mm ./data/herstappe/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff
```

<div class="alert alert-info" style="font-size:120%">

**REMEMBER**: <br>

The [`gdal` library](https://gdal.org/) is a very powerful set of functions. It is the
open source Swiss Army knife for raster and vector geospatial data handling. GDAL provides Python bindings to run it from Python code, but these are not very 'Pythonic'. When familiar with the command line the [command line raster functions](https://gdal.org/programs/index.html#raster-programs) (CLI) are certainly worthwhile to check out!
    
You can run a CLI command inside a Jupyter Notebook by prefixing it with the `!` character.

</div>

+++

Important information we get from the `gdalinfo` command are 

* Coordinate reference system (CRS), see also [02-coordinate-reference-systems notebook](./02-coordinate-reference-systems.ipynb).
* Number of bands in the data set: A data set can contain one (single) or more (multi) layers (bands).
* Spatial resolution: This resolution represents the area on the ground that each pixel covers. The units for your data are determined by the CRS above (e.g. meters).
* Spatial extent (bounding box) of the data: The geographic area that the raster data covers.

<img src="../img/raster-spatial-extent-coordinates.png" alt="spatial-extnet" style="width:500px;"/>

<small>_Image Source: National Ecological Observatory Network (NEON)._</small>

+++

Let's see how Rasterio interprets this information: 

```{code-cell} ipython3
src = rasterio.open(file_herstappe)
```

```{code-cell} ipython3
src.meta
```

The `meta` attribute contains some of the essential spatial information, whereas the `profile` attribute contains the spatial metadata combined with the metadata about the GeoTiff storage:

```{code-cell} ipython3
src.profile
```

Some of these are also stored in a separate attribute:

```{code-cell} ipython3
src.crs, src.count
```

```{code-cell} ipython3
src.crs == src.meta["crs"]
```

The `meta` attribute misses information on the spatial resolution and spatial extent, available in separate attributes:

```{code-cell} ipython3
src.res
```

```{code-cell} ipython3
src.bounds
```

Geotiff files can also contain a data mask to define which pixels contain valid data and which are no data. Raster data often has such a `NoDataValue`. To extract the mask, use the `dataset_mask` method, which returns 255 for valid data and 0 for nodata:

```{code-cell} ipython3
src.dataset_mask()
```

We should not forget to close the file afterwards!

```{code-cell} ipython3
src.close()
```

## Using context manager to open files

A better approach instead of opening and closing the data file separately is to use a Python [context manager](https://docs.python.org/3/reference/compound_stmts.html#with):

```{code-cell} ipython3
with rasterio.open(file_herstappe) as src:
    print(src)
```

```{code-cell} ipython3
print(src)
```

A __context manager__ allows you to open the data and work with it. Within the context manager, Python makes a temporary connection to the file that you are trying to open. 

The `with` statement creates a connection to the file that you want to open. The __default connection type is read only__. This means that you can NOT modify that file by default. Not being able to modify the original data is a good thing because it prevents you from making unintended changes to your original data.

Opening and closing files using rasterio and context managers is efficient as it establishes a connection to the raster file rather than directly reading it into memory. Once you are done opening and reading in the data, the context manager closes that connection to the file.

+++

By extracting the information we require inside the context manager, we are able to work with it outside the context:

```{code-cell} ipython3
with rasterio.open(file_herstappe) as src:
    herstappe_meta = src.meta
    herstappe_bounds =  src.bounds
```

```{code-cell} ipython3
herstappe_bounds, herstappe_meta
```

__Note:__ The usage of context managers is a default Python feature and good advice when interacting with files.

```{raw-cell}
with open("../README.md") as md_file:
    test = md_file.readline()
```

<div class="alert alert-info" style="font-size:120%">

**REMEMBER**: <br>

When interacting with file on disk, use the `with` statement to open it within a so-called __context manager__. This makes sure the connection to your file is properly closed! 

</div>

+++

## What about the data itself?

+++

We started this notebook with reading and plotting the Herstappe data of 2018-09-18:

```{code-cell} ipython3
with rasterio.open(file_herstappe) as src:
    herstappe = src.read()
    show(herstappe)  #, transform=src.transform)
```

Within the context manager (the `with` statement) we use the `read()` method to load the data itself from the file and assign this to the `herstappe` variable. As with the metadata, the data is stored in computer memory and we can work with the data (without affecting the original data on file):

+++

The `show` method is a convenience plotting function provided by the Rasterio Python package. By adding the `transform=src.transform` we get the information of the spatial extent as the x and y axis labels of the plot. We will later learn about other functionalities of Rasterio. 

```{code-cell} ipython3
herstappe
```

The variable `herstappe` does not contains any spatial context, but is a 2D array with numeric (float) values. Let's check the data type of this variable:

```{code-cell} ipython3
type(herstappe)
```

When you read raster data using Rasterio you are actually creating a __Numpy array__. A Numpy array does not store spatial information, but is an efficient data type to calculate with arrays in general:

```{code-cell} ipython3
herstappe.shape
```

```{code-cell} ipython3
herstappe / 10
```

```{code-cell} ipython3
herstappe.shape
```

```{code-cell} ipython3
herstappe.min(), herstappe.max()
```

```{code-cell} ipython3
import matplotlib.pyplot as plt
```

```{code-cell} ipython3
plt.hist(herstappe.flatten(), bins=25);
```

[Numpy](https://numpy.org/) is a fundamental package for scientific computing in the scientific Python ecosystem. Many other packages rely on Numpy as well (Pandas, GeoPandas,...). The bridge in between raster data sets and Numpy enable us to apply the full power of Numpy to spatial data. In the following notebook we will focus on the Numpy package. 

But let's finish this section with some exercises on reading raster data.

+++

<div class="alert alert-success">

**EXERCISE**:

The Geotiff file `./data/gent/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff` is True color data set downloaded from [sentinel-hub](https://www.sentinel-hub.com/). Check the metadata of the file using the `gdalinfo` command and find out:
    
* How many pixels contains the data set?
* How many bands does the data set consist of?
* What is the CRS of the data set?
* What is the resolution of the data set?
    
How is the data set different from the Herstappe data set?
    
<details><summary>Hint</summary>

Any command that works at the command-line can be used in IPython/Jupyter by prefixing it with the `!` character, e.g. `!ls`

</details>

</div>

```{code-cell} ipython3
:clear_cell: true

!gdalinfo ./data/gent/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff
```

<div class="alert alert-success">

**EXERCISE**:

Make a __plot of the FIRST channel__ of the data stored in the Geotiff file `./data/gent/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff`.
    
<details><summary>Hints</summary>

- Make sure to use a context manager to access the data files!
- You only need the data of the first band. Check the documentation of the `read` method to see how.
- There are multiple ways of plotting raster data. For this exercise, use the `show` method provide by Rasterio. Make sure the spatial extent information is used as x and y axis labels.

</details>    

</div>

```{code-cell} ipython3
:clear_cell: true

gent_file = "./data/gent/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff"
with rasterio.open(gent_file) as gent_gif:
    gent = gent_gif.read([1]) # only read the first band/layer
    show(gent, transform=gent_gif.transform)
```

<div class="alert alert-success">

**EXERCISE**:

Using Rasterio, read the spatial extent and resolution from two Geotiff example files and assign it to variables:
    
- Geotiff file `./data/gent/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff`: assign the spatial extent to a variable `gent_extent` and the resolution to `gent_res`
- `./data/herstappe/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff`: assign the spatial extent to a variable `herstappe_extent` and the resolution to `herstappe_res` 
    
Do both datasets have the same resolution? 
    
Without doing the calculation, discuss with your neighbours (or break out colleagues) __how__ you would define which data set covers the largest area?
    
<details><summary>Hint</summary>

Make sure to use a context manager to access the data files!

</details>    

</div>

```{code-cell} ipython3
:clear_cell: true

gent_file = "./data/gent/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff"
with rasterio.open(gent_file) as src:
    gent_extent = src.bounds
    gent_res = src.res
gent_res, gent_extent
```

```{code-cell} ipython3
:clear_cell: true

herstappe_file = "./data/herstappe/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff"
with rasterio.open(herstappe_file) as src:
    herstappe_extent = src.bounds
    herstappe_res = src.res
herstappe_res, herstappe_extent
```

```{code-cell} ipython3

```
