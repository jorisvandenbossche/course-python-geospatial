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

<p><font size="6"><b> Raster operations and raster-vector tools</b></font></p>


> *DS Python for GIS and Geoscience*  
> *October, 2020*
>
> *© 2020, Joris Van den Bossche and Stijn Van Hoey. Licensed under [CC BY 4.0 Creative Commons](http://creativecommons.org/licenses/by/4.0/)*

---

+++

In the previous notebooks, we mostly worked with either vector data or raster data. 
But, often you will encounter both types of data and will have to combine them.
In this notebook, we show *some* examples of raster/vector interactions.

```{code-cell} ipython3
import pandas as pd
import numpy as np
import geopandas
import rasterio

import xarray as xr

import matplotlib.pyplot as plt
```

# `rioxarray`: xarray extension based on rasterio

+++

In the previous notebooks, we already used `rasterio` (https://rasterio.readthedocs.io/en/latest/) to read raster files such as GeoTIFFs (through the `xarray.open_rasterio()` function). Rasterio provides support for reading and writing geospatial raster data as numpy N-D arrays, mainly through bindings to the GDAL library. 

In addition, rasterio provides a Python API to perform some GIS raster operations (clip, mask, warp, merge, transformation,...) and can be used to only load a subset of a large dataset into memory. However, the main complexity in using `rasterio`, is that the spatial information is decoupled from the data itself (i.e. the numpy array). This means that you need to keep track and organize the extent and metadata throughout the operations (e.g. the "transform") and you need to keep track of what each dimension represents (y-first, as arrays are organized along rows first). Notebook [12-rasterio.ipynb](12-rasterio.ipynb) goes into more depth on the rasterio package itself. 



Enter `rioxarray` (https://corteva.github.io/rioxarray/stable/index.html), which extends xarray with geospatial functionality powered by rasterio.

```{code-cell} ipython3
import rioxarray
```

```{code-cell} ipython3
data_file = "./data/herstappe/raster/2020-09-17_Sentinel_2_L1C_True_color.tiff"
```

```{code-cell} ipython3
data = rioxarray.open_rasterio(data_file)
data
```

The `rioxarray.open_rasterio` function is similar to `xarray.open_rasterio`, but in addition adds a `spatial_ref` coordinate to keep track of the spatial reference information.

Once `rioxarray` is imported, it also provides a `.rio` accessor on the xarray.DataArray object, which gives access to some properties of the raster data:

```{code-cell} ipython3
data.rio.crs
```

```{code-cell} ipython3
data.rio.bounds()
```

```{code-cell} ipython3
data.rio.resolution()
```

```{code-cell} ipython3
data.rio.nodata
```

It provides a handy method to reproject a raster:

```{code-cell} ipython3
data.rio.reproject("EPSG:31370").plot.imshow(figsize=(10,6))
```

```{code-cell} ipython3
from rasterio.enums import Resampling
```

```{code-cell} ipython3
data.rio.reproject("EPSG:31370", resampling=Resampling.bilinear).plot.imshow(figsize=(10,6))
```

Or downsample at the same time:

```{code-cell} ipython3
data.rio.reproject(data.rio.crs, resolution=120, resampling=Resampling.cubic).plot.imshow(figsize=(10,6))
```

## Extract the data you need

+++

In many applications, a specific research area is used. Extracting the data you need from a given raster data set by a vector (polygon) file is a common operation in GIS analysis. We use the clipping example to explain the typical workflow with rioxarray / rasterio.

For our Herstappe example, the study area is available as vector data `./data/herstappe/vector/herstappe.geojson`:

```{code-cell} ipython3
herstappe_vect = geopandas.read_file("./data/herstappe/vector/herstappe.geojson")
herstappe_vect
```

```{code-cell} ipython3
herstappe_vect.plot()
```

```{code-cell} ipython3
herstappe_vect.crs
```

Make sure both data sets are defined in the same CRS and extracting the geometry can be used as input for the masking:

```{code-cell} ipython3
herstappe_vect = herstappe_vect.to_crs(epsg=3857)
```

```{code-cell} ipython3
clipped = data.rio.clip(herstappe_vect.geometry)
```

```{code-cell} ipython3
fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(10,4))
data.plot.imshow(ax=ax1)
herstappe_vect.plot(ax=ax1, facecolor="none", edgecolor="red")
clipped.plot.imshow(ax=ax2)
fig.tight_layout()
```

The above uses the `rasterio` package (with the `mask` and `geometry_mask` / `rasterize` functionality) under the hood. This simplifies the operation compared to directly using `rasterio`.


```python
# cfr. The Rasterio workflow

from rasterio.mask import mask

# 1 - Open a data set using the context manager
with rasterio.open(data_file) as src: 

    # 2 - Read and transform the data set by clipping
    out_image, out_transform = mask(src, herstappe_vect.geometry, crop=True)
    
    # 3 - Update the spatial metadata/profile of the data set
    herstappe_profile = src.profile
    herstappe_profile.update({"height": out_image.shape[1],
                              "width": out_image.shape[2],
                              "transform": out_transform})
    # 4 - Save the new data set with the updated metadata/profile                   
    with rasterio.open("./herstappe_masked.tiff", "w", **herstappe_profile) as dest: 
        dest.write(out_image)
```

The [12-rasterio.ipynb](12-rasterio.ipynb) notebook explains this workflow in more detail.

One important difference, though, is that the above `rasterio` workflow will not load the full raster into memory when only loading (clipping) a small part of it. This can also be achieved in `rioxarray` with the `from_disk` keyword.

+++

## Convert vector to raster

+++

### Load DEM raster and river vector data

+++

As example, we are using data from the Zwalm river area in Flanders. 

The digital elevation model (DEM) can be downloaded via the [governmental website](https://download.vlaanderen.be/Producten/Detail?id=936&title=Digitaal_Hoogtemodel_Vlaanderen_II_DSM_raster_5_m) ([download link](https://downloadagiv.blob.core.windows.net/dhm-vlaanderen-ii-dsm-raster-5m/DHMVIIDSMRAS5m_k30.zip), extracted in the `/data` directory for this example)/

```{code-cell} ipython3
dem_zwalm_file = "data/DHMVIIDSMRAS5m_k30/GeoTIFF/DHMVIIDSMRAS5m_k30.tif"
```

```{code-cell} ipython3
dem_zwalm = xr.open_rasterio(dem_zwalm_file).sel(band=1)
```

```{code-cell} ipython3
img = dem_zwalm.plot.imshow(
    cmap="terrain", figsize=(10, 4), interpolation='antialiased')
img.axes.set_aspect("equal")
```

Next, we download the shapes of the rivers in the area through a WFS (Web Feature Service):

```{code-cell} ipython3
import json
import requests

wfs_rivers = "https://geoservices.informatievlaanderen.be/overdrachtdiensten/VHAWaterlopen/wfs"
params = dict(service='WFS', version='1.1.0', request='GetFeature',
              typeName='VHAWaterlopen:Wlas', outputFormat='json',
              cql_filter="(VHAZONENR=460)OR(VHAZONENR=461)", srs="31370")

# Fetch data from WFS using requests
r = requests.get(wfs_rivers, params=params)
```

And convert this to a GeoDataFrame:

```{code-cell} ipython3
# Create GeoDataFrame from geojson
segments = geopandas.GeoDataFrame.from_features(json.loads(r.content), crs="epsg:31370")
```

```{code-cell} ipython3
segments.head()
```

```{code-cell} ipython3
segments.plot(figsize=(8, 7))
```

### Clip raster with vector

The catchment extent is much smaller than the DEM file, so clipping the data first will make the computation less heavy.

+++

Let's first download the catchment area of the Zwalm river from the Flemish government:

```{code-cell} ipython3
import json
import requests

wfs_bekkens = "https://geoservices.informatievlaanderen.be/overdrachtdiensten/Watersystemen/wfs"
params = dict(service='WFS', version='1.1.0', request='GetFeature',
              typeName='Watersystemen:WsDeelbek', outputFormat='json',
              cql_filter="DEELBEKNM='Zwalm'", srs="31370")

# Fetch data from WFS using requests
r = requests.get(wfs_bekkens, params=params)
catchment = geopandas.GeoDataFrame.from_features(json.loads(r.content), crs="epsg:31370")
```

```{code-cell} ipython3
catchment
```

Save to a file for later reuse:

```{code-cell} ipython3
# save to file
catchment = catchment.to_crs('epsg:4326') # geojson is default 4326
catchment.to_file("./data/zwalmbekken.geojson", driver="GeoJSON")
```

```{code-cell} ipython3
geopandas.read_file("./data/zwalmbekken.geojson").plot()
```

#### 1. Using rioxarray (rasterio)

+++

As shown above, we can use rioxarray to clip the raster file:

```{code-cell} ipython3
dem_zwalm = xr.open_rasterio(dem_zwalm_file).sel(band=1)
dem_zwalm
```

```{code-cell} ipython3
clipped = dem_zwalm.rio.clip(catchment.to_crs('epsg:31370').geometry)
```

Using rioxarray's `to_raster()` method, we can also save the result to a new GeoTIFF file:

```{code-cell} ipython3
clipped.rio.to_raster("./dem_masked_rio.tiff")
```

This DEM raster file used -9999 as the NODATA value, and this is therefore also used for the clipped result:

```{code-cell} ipython3
clipped.rio.nodata
```

```{code-cell} ipython3
img = clipped.where(clipped != -9999).plot.imshow(
    cmap='terrain', figsize=(10, 6), interpolation='antialiased')
img.axes.set_aspect("equal")
```

With rioxarray, we can also convert nodata values to NaNs (and thus using float dtype) when loading the raster data:

```{code-cell} ipython3
dem_zwalm2 = rioxarray.open_rasterio(dem_zwalm_file, masked=True).sel(band=1)
```

```{code-cell} ipython3
dem_zwalm2.rio.nodata
```

```{code-cell} ipython3
dem_zwalm2.rio.clip(catchment.to_crs('epsg:31370').geometry)
```

If we want to avoid loading the full original raster data, the `from_disk` keyword can be used.

```{code-cell} ipython3
dem_zwalm2.rio.clip(catchment.to_crs('epsg:31370').geometry, from_disk=True)
```

#### 2. Using GDAL CLI

+++

If we have the raster and vector files on disk, [`gdal CLI`](https://gdal.org/programs/index.html) will be very fast to work with (note that GDAL automatically handles the CRS difference of the raster and vector).

```{code-cell} ipython3
rm ./dem_masked_gdal.tiff
```

```{code-cell} ipython3
!gdalwarp -cutline ./data/zwalmbekken.geojson -crop_to_cutline data/DHMVIIDSMRAS5m_k30/GeoTIFF/DHMVIIDSMRAS5m_k30.tif ./dem_masked_gdal.tiff
```

```{code-cell} ipython3
clipped_gdal = rioxarray.open_rasterio("./dem_masked_gdal.tiff", masked=True).sel(band=1)
img = clipped_gdal.plot.imshow(
    cmap="terrain", figsize=(10, 6), interpolation='antialiased')
img.axes.set_aspect("equal")
```

### Convert vector to raster

+++

To create a raster with the vector "burned in", we can use the `rasterio.features.rasterize` function. This expects a list of (shape, value) tuples, and an output image shape and transform. Here, we will create a new raster image with the same shape and extent as the DEM above. And we first take a buffer of the river lines:

```{code-cell} ipython3
import rasterio.features
```

```{code-cell} ipython3
segments_buffered = segments.geometry.buffer(100)
img = rasterio.features.rasterize(
    segments_buffered, 
    out_shape=clipped.shape, 
    transform=clipped.rio.transform())
```

```{code-cell} ipython3
img
```

```{code-cell} ipython3
fig, (ax0, ax1) = plt.subplots(1, 2)
ax0.imshow(img*50)
ll = ax1.imshow(clipped.values - img*20, vmin=0, cmap="terrain") # just as an example
plt.tight_layout()
```

## Extracting values from rasters based on vector data

The **rasterstats** package provides methods to calculate summary statistics of geospatial raster datasets based on vector geometries (https://github.com/perrygeo/python-rasterstats)

+++

To illustrate this, we are reading a raster file with elevation data of the full world (the file contains a single band for the elevation, save the file in the `data` subdirectory; [download link](https://www.eea.europa.eu/data-and-maps/data/world-digital-elevation-model-etopo5/zipped-dem-geotiff-raster-geographic-tag-image-file-format-raster-data/zipped-dem-geotiff-raster-geographic-tag-image-file-format-raster-data/at_download/file)):

```{code-cell} ipython3
countries = geopandas.read_file("zip://./data/ne_110m_admin_0_countries.zip")
cities = geopandas.read_file("zip://./data/ne_110m_populated_places.zip")
```

```{code-cell} ipython3
dem_geotiff = "data/raw/DEM_geotiff/alwdgg.tif"
```

```{code-cell} ipython3
img = xr.open_rasterio(dem_geotiff).sel(band=1).plot.imshow(cmap="terrain", figsize=(10, 4), )
img.axes.set_aspect("equal")
```

Given this raster of the elevation, we might want to know the elevation at a certain location or for each country.
For the countries example, we want to extract the pixel values that fall within a country polygon, and calculate a statistic for it, such as the mean or the maximum.

Such functionality to extract information from a raster for given vector data is provided by the rasterstats package.

```{code-cell} ipython3
import rasterstats
```

For extracting the pixel values for polygons, we use the `zonal_stats` function, passing it the GeoSeries, the path to the raster file, and the method to compute the statistics.

```{code-cell} ipython3
result = rasterstats.zonal_stats(countries.geometry, dem_geotiff,
                                 stats=['min', 'mean', 'max'])
```

The results can be assigned to new columns:

```{code-cell} ipython3
countries[['min', 'max', 'mean']] = pd.DataFrame(result)
```

```{code-cell} ipython3
countries.head()
```

And then we can sort by the average elevation of the country:

```{code-cell} ipython3
countries.sort_values('mean', ascending=False).head()
```

For points, a similar function called `point_query` can be used (specifying the interpolation method):

```{code-cell} ipython3
cities["elevation"] = rasterstats.point_query(cities.geometry, 
                                              dem_geotiff, interpolate='bilinear')
```

```{code-cell} ipython3
cities.sort_values(by="elevation", ascending=False).head()
```

-----------

### A bit more about WFS

> The Web Feature Service (WFS) represents a change in the way geographic information is created, modified and exchanged on the Internet. Rather than sharing geographic information at the file level using File Transfer Protocol (FTP), for example, the WFS offers direct fine-grained...

(https://www.ogc.org/standards/wfs)

In brief, the WFS is the specification to __access and download vector datasets__.

To access WFS data, you need the following information:
- URL of the service, e.g. `https://geoservices.informatievlaanderen.be/overdrachtdiensten/VHAWaterlopen/wfs`. Looking for these URLS, check [WFS page of Michel Stuyts](https://wfs.michelstuyts.be/?lang=en)
- The available projections and layers, also check [WFS page of Michel Stuyts](https://wfs.michelstuyts.be/?lang=en) or start looking into the `GetCapabilities`, e.g. [vha waterlopen](https://geoservices.informatievlaanderen.be/overdrachtdiensten/VHAWaterlopen/wfs?REQUEST=GetCapabilities&SERVICE=WFS)

Instead of downloading the entire data set, filtering the request itself (only downloading what you need) is a good idea, using the `cql_filter` filter. Finding out these is sometimes a bit of hazzle... E.g. quickly [preview the data in QGIS](https://docs.qgis.org/3.10/en/docs/training_manual/online_resources/wfs.html?highlight=wfs).

You can also use the [`OWSLib` library](https://geopython.github.io/OWSLib/#wfs). But as WFS is a webservice, the `requests` package will be sufficient for simple queries.

+++

As an example - municipalities in Belgium, see https://wfs.michelstuyts.be/service.php?id=140&lang=en, _WFS Voorlopig referentiebestand gemeentegrenzen 2019_

- URL of the service: https://geoservices.informatievlaanderen.be/overdrachtdiensten/VRBG2019/wfs
- Available projections:  EPSG:4258, EPSG:3812,...
- Available layers: VRBG2019:Refgem:,  VRBG2019:Refarr:,...
- Column `Naam` contains the municipatility, e.g. `Gent`

```{code-cell} ipython3
wfs_municipality = "https://geoservices.informatievlaanderen.be/overdrachtdiensten/VRBG2019/wfs"
params = dict(service='WFS', version='1.1.0', request='GetFeature',
              typeName='VRBG2019:Refgem', outputFormat='json',
              cql_filter="NAAM='Gent'", srs="31370")

# Fetch data from WFS using requests
r = requests.get(wfs_municipality, params=params)
gent = geopandas.GeoDataFrame.from_features(json.loads(r.content), crs="epsg:31370")
gent.plot()
```

```{code-cell} ipython3

```

## Cloud: only download what you need

Rasterio/rioxarray only reads the data from disk that is requested to overcome loading entire data sets into memory. The same applies to downloading data, overcoming entire downloads when only a fraction is required (when the online resource supports this). An example is https://zenodo.org/record/2654620, which is available as [Cloud Optimized Geotiff (COG)](https://www.cogeo.org/). Also cloud providers (AWS, google,...) do support COG files, e.g. [Landstat images](https://docs.opendata.aws/landsat-pds/readme.html).

These files are typically very large to download, whereas we might only need a small subset of the data. COG files support downloading a subset of the data you need using the masking approach.

Let's use the Averbode nature reserve data as an example, available at the URL: http://s3-eu-west-1.amazonaws.com/lw-remote-sensing/cogeo/20160401_ABH_1_Ortho.tif

```{code-cell} ipython3
averbode_cog_rgb = 'http://s3-eu-west-1.amazonaws.com/lw-remote-sensing/cogeo/20160401_ABH_1_Ortho.tif'
```

Check the metadata, without downloading the data itself:

```{code-cell} ipython3
averbode_data = rioxarray.open_rasterio(averbode_cog_rgb)
```

```{code-cell} ipython3
averbode_data
```

```{code-cell} ipython3
with rasterio.open(averbode_cog_rgb) as averbode:
    print(averbode.meta)
```

Downloading the entire data set would be 37645*35405\*4 pixels of 1 byte, so more or less 5.3 GByte

```{code-cell} ipython3
37645*35405*4 / 1e9  # Gb
```

```{code-cell} ipython3
averbode_data.size / 1e9  # Gb
```

Assume that we have a study area which is much smaller than the total extent of the available image:

```{code-cell} ipython3
left, bottom, right, top = averbode_data.rio.bounds()
```

```{code-cell} ipython3
averbode_study_area = geopandas.read_file("./data/averbode/study_area.geojson")
ax = averbode_study_area.plot();
ax.set_xlim(left, right);
ax.set_ylim(bottom, top);
```

In the case of COG data, the data can sometimes be requested on different resolution levels when stored as such. So, to get a very broad overview of the data, we can request the coarsest resolution by resampling and download the data at the resampled resolution:

```{code-cell} ipython3
with rasterio.open(averbode_cog_rgb) as src:
    print(f"Available resolutions are {src.overviews(1)}")
```

```{code-cell} ipython3
averbode_254 = rioxarray.open_rasterio(averbode_cog_rgb, overview_level=7)
```

```{code-cell} ipython3
averbode_254.size / 1e6
```

```{code-cell} ipython3
averbode_254.rio.resolution()
```

Compare the thumbnail version of the data with our study area:

```{code-cell} ipython3
fig, ax = plt.subplots()
averbode_254.sel(band=[1, 2, 3]).plot.imshow(ax=ax)
averbode_study_area.plot(ax=ax, color='None', edgecolor='red', linewidth=2);
```

Downloading the entire data file would be overkill. Instead, we only want to download the data of the study area:

```{code-cell} ipython3
output_file = "./averbode_orthophoto.tiff"
```

The resulting data set will still be around 35MB and will take a bit of time, but this is only a fraction of the original data file:

```{code-cell} ipython3
%%time
# Only run this cell when sufficient band width ;-)
with rasterio.open(averbode_cog_rgb) as averbode_rgb:
    averbode_rgb_image, averbode_rgb_transform = rasterio.mask.mask(averbode_rgb, averbode_study_area.geometry, crop=True)
    averbode_rgb_profile = averbode_rgb.profile  

    averbode_rgb_profile.update({"driver": "GTiff",
                                 "height": averbode_rgb_image.shape[1],
                                 "width": averbode_rgb_image.shape[2],
                                 "transform": averbode_rgb_transform
                                })
    
    with rasterio.open(output_file, "w", **averbode_rgb_profile) as dest:
        dest.write(averbode_rgb_image)
```

```{code-cell} ipython3
averbode_subset = rioxarray.open_rasterio(output_file)
averbode_subset
```

```{code-cell} ipython3
averbode_subset.size / 1e9
```

```{code-cell} ipython3
averbode_subset.sel(band=[1, 2, 3]).plot.imshow(figsize=(10, 10))
```

```{code-cell} ipython3

```

Thanks to https://geohackweek.github.io/raster/04-workingwithrasters/ for the inspiration
