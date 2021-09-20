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

<p><font size="6"><b> Raster - vector tools</b></font></p>


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
from rasterio.plot import show

import matplotlib.pyplot as plt
```

```{code-cell} ipython3
countries = geopandas.read_file("zip://./data/ne_110m_admin_0_countries.zip")
cities = geopandas.read_file("zip://./data/ne_110m_populated_places.zip")
```

## Extracting values from rasters based on vector data

The **rasterstats** package provides methods to calculate summary statistics of geospatial raster datasets based on vector geometries (https://github.com/perrygeo/python-rasterstats)

+++

To illustrate this, we are reading a raster file with elevation data of the full world (the file contains a single band for the elevation, save the file in the `data` subdirectory; [download link](https://www.eea.europa.eu/data-and-maps/data/world-digital-elevation-model-etopo5/zipped-dem-geotiff-raster-geographic-tag-image-file-format-raster-data/zipped-dem-geotiff-raster-geographic-tag-image-file-format-raster-data/at_download/file)):

```{code-cell} ipython3
dem_geotiff = "data/raw/dem_geotiff/DEM_geotiff/alwdgg.tif"
```

```{code-cell} ipython3
with rasterio.open(dem_geotiff) as src:
    print(src.meta)
    fig, ax = plt.subplots(figsize=(10, 6))
    show(src, ax=ax, cmap='terrain')
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
with rasterio.open(dem_zwalm_file) as src:
    print(src.meta)
    fig, ax = plt.subplots(figsize=(10, 6))
    #dem_zwalm = src.read(1)
    show(src, ax=ax, cmap='terrain')
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

_See also notebook `12-rasterio.ipynb`_

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
del catchment["bbox"]
catchment.to_file("./data/zwalmbekken.geojson", driver="GeoJSON")
```

```{code-cell} ipython3
geopandas.read_file("./data/zwalmbekken.geojson").plot()
```

### 1. Using Rasterio

```{code-cell} ipython3
from rasterio.mask import mask
```

```{code-cell} ipython3
# cfr. The Rasterio workflow
with rasterio.open(dem_zwalm_file) as src: # 1

    # 2
    out_image, out_transform = mask(src, 
        catchment.to_crs('epsg:31370').geometry, crop=True)
    
    # 3
    zwalm_profile = src.profile
    zwalm_profile.update({"height": out_image.shape[1],
                          "width": out_image.shape[2],
                          "transform": out_transform})  
    # 4                              
    with rasterio.open("./dem_masked.tiff", "w", **zwalm_profile) as dest: 
        dest.write(out_image)
```

Check the output of the clipping:

```{code-cell} ipython3
with rasterio.open("./dem_masked.tiff") as src:
    print(src.meta)
    dem_meta = src.meta
    transform =src.transform    
    fig, ax = plt.subplots(figsize=(10, 6))
    dem_zwalm = src.read(1)
    show(src, ax=ax, cmap='terrain')
```

### 2. Using GDAL CLI

+++

If we have the raster and vector files on disk, [`gdal CLI`](https://gdal.org/programs/index.html) will be very fast to work with (note that GDAL automatically handles the CRS difference of the raster and vector).

```{code-cell} ipython3
!gdalwarp -cutline ./data/zwalmbekken.geojson -crop_to_cutline data/DHMVIIDSMRAS5m_k30/GeoTIFF/DHMVIIDSMRAS5m_k30.tif ./dem_masked_gdal.tiff
```

```{code-cell} ipython3
with rasterio.open("./dem_masked_gdal.tiff") as src:
    print(src.meta)
    fig, ax = plt.subplots(figsize=(10, 6))
    show(src, ax=ax, cmap='terrain')
```

### Convert vector to raster

+++

To create a raster with the vector "burned in", we can use the `rasterio.features.rasterize` function. This expects a list of (shape, value) tuples, and an output image shape and transform. Here, we will create a new raster image with the same shape and extent as the DEM above. And we first take a buffer of the river lines:

```{code-cell} ipython3
segments_buffered = segments.geometry.buffer(100)
img = rasterio.features.rasterize(
    zip(segments_buffered, [1]*len(segments_buffered)), 
    out_shape=(3051, 2405), 
    transform=transform)
```

```{code-cell} ipython3
fig, (ax0, ax1) = plt.subplots(1, 2)
ax0.imshow(img*50)
ll = ax1.imshow(dem_zwalm - img*20) # just as an example
plt.tight_layout()
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

-----------
-----------

```{code-cell} ipython3

```
