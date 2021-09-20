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

<p><font size="6"><b>Coordinate reference systems</b></font></p>


> *DS Python for GIS and Geoscience*  
> *October, 2020*
>
> *© 2020, Joris Van den Bossche and Stijn Van Hoey  (<mailto:jorisvandenbossche@gmail.com>, <mailto:stijnvanhoey@gmail.com>). Licensed under [CC BY 4.0 Creative Commons](http://creativecommons.org/licenses/by/4.0/)*

---

```{code-cell} ipython3
%matplotlib inline

import pandas as pd
import geopandas
```

```{code-cell} ipython3
countries = geopandas.read_file("data/ne_110m_admin_0_countries.zip")
cities = geopandas.read_file("data/ne_110m_populated_places.zip")
rivers = geopandas.read_file("data/ne_50m_rivers_lake_centerlines.zip")
```

## Coordinate reference systems

Up to now, we have used the geometry data with certain coordinates without further wondering what those coordinates mean or how they are expressed.

> The **Coordinate Reference System (CRS)** relates the coordinates to a specific location on earth.

For an in-depth explanation, see https://docs.qgis.org/2.8/en/docs/gentle_gis_introduction/coordinate_reference_systems.html

+++

### Geographic coordinates

> Degrees of latitude and longitude.
>
> E.g. 48°51′N, 2°17′E

The most known type of coordinates are geographic coordinates: we define a position on the globe in degrees of latitude and longitude, relative to the equator and the prime meridian. 
With this system, we can easily specify any location on earth. It is used widely, for example in GPS. If you inspect the coordinates of a location in Google Maps, you will also see latitude and longitude.

**Attention!**

in Python we use (lon, lat) and not (lat, lon)

- Longitude: [-180, 180]{{1}}
- Latitude: [-90, 90]{{1}}

+++

### Projected coordinates

> `(x, y)` coordinates are usually in meters or feet

Although the earth is a globe, in practice we usually represent it on a flat surface: think about a physical map, or the figures we have made with Python on our computer screen.
Going from the globe to a flat map is what we call a *projection*.

![](../img/projection.png)

We project the surface of the earth onto a 2D plane so we can express locations in cartesian x and y coordinates, on a flat surface. In this plane, we then typically work with a length unit such as meters instead of degrees, which makes the analysis more convenient and effective.

However, there is an important remark: the 3 dimensional earth can never be represented perfectly on a 2 dimensional map, so projections inevitably introduce distortions. To minimize such errors, there are different approaches to project, each with specific advantages and disadvantages.

Some projection systems will try to preserve the area size of geometries, such as the Albers Equal Area projection. Other projection systems try to preserve angles, such as the Mercator projection, but will see big distortions in the area. Every projection system will always have some distortion of area, angle or distance.

<table><tr>
<td> <img src="../img/projections-AlbersEqualArea.png"/> </td>
<td> <img src="../img/projections-Mercator.png"/> </td>
</tr>
<tr>
<td> <img src="../img/projections-Robinson.png"/> </td>
</tr></table>

+++

**Projected size vs actual size (Mercator projection)**:

![](../img/mercator_projection_area.gif)

+++

## Coordinate Reference Systems in Python / GeoPandas

+++

A GeoDataFrame or GeoSeries has a `.crs` attribute which holds (optionally) a description of the coordinate reference system of the geometries:

```{code-cell} ipython3
countries.crs
```

For the `countries` dataframe, it indicates that it uses the EPSG 4326 / WGS84 lon/lat reference system, which is one of the most used for geographic coordinates.


It uses coordinates as latitude and longitude in degrees, as can you be seen from the x/y labels on the plot:

```{code-cell} ipython3
countries.plot()
```

The `.crs` attribute returns a `pyproj.CRS` object. To specify a CRS, we typically use some string representation:


- **EPSG code**
  
  Example: `EPSG:4326` = WGS84 geographic CRS (longitude, latitude)
  
- **Well-Know-Text (WKT)** representation

- In older software and datasets, you might also encounter a "`proj4` string" representation:
  
  Example: `+proj=longlat +datum=WGS84 +no_defs`

  This is however no longer recommended.


See eg https://epsg.io/4326

Under the hood, GeoPandas uses the `pyproj` / `PROJ` libraries to deal with the re-projections.

For more information, see also http://geopandas.readthedocs.io/en/latest/projections.html.

+++

### Transforming to another CRS

We can convert a GeoDataFrame to another reference system using the `to_crs` function. 

For example, let's convert the countries to the World Mercator projection (http://epsg.io/3395):

```{code-cell} ipython3
# remove Antartica, as the Mercator projection cannot deal with the poles
countries = countries[(countries['name'] != "Antarctica")]
```

```{code-cell} ipython3
countries_mercator = countries.to_crs(epsg=3395)  # or .to_crs("EPSG:3395")
```

```{code-cell} ipython3
countries_mercator.plot()
```

Note the different scale of x and y.

+++

### Why using a different CRS?

There are sometimes good reasons you want to change the coordinate references system of your dataset, for example:

- Different sources with different CRS -> need to convert to the same crs

    ```python
    df1 = geopandas.read_file(...)
    df2 = geopandas.read_file(...)

    df2 = df2.to_crs(df1.crs)
    ```

- Mapping (distortion of shape and distances)

- Distance / area based calculations -> ensure you use an appropriate projected coordinate system expressed in a meaningful unit such as meters or feet (not degrees).

<div class="alert alert-info" style="font-size:120%">

**ATTENTION:**

All the calculations that happen in GeoPandas and Shapely assume that your data is in a 2D cartesian plane, and thus the result of those calculations will only be correct if your data is properly projected.

</div>

+++

## Let's practice!

Again, we will go back to the Paris datasets. Up to now, we provided the datasets in an appropriate projected CRS for the exercises. But the original data were actually using geographic coordinates. In the following exercises, we will start from there.

---

+++

Going back to the Paris districts dataset, this is now provided as a GeoJSON file (`"data/paris_districts.geojson"`) in geographic coordinates.

For converting to projected coordinates, we will use the standard projected CRS for France is the RGF93 / Lambert-93 reference system, referenced by the `EPSG:2154` number (in Belgium this would be Lambert 72, EPSG:31370).

<div class="alert alert-success">

**EXERCISE: Projecting a GeoDataFrame**

* Read the districts datasets (`"data/paris_districts.geojson"`) into a GeoDataFrame called `districts`.
* Look at the CRS attribute of the GeoDataFrame. Do you recognize the EPSG number?
* Make a plot of the `districts` dataset.
* Calculate the area of all districts.
* Convert the `districts` to a projected CRS (using the `EPSG:2154` for France). Call the new dataset `districts_RGF93`.
* Make a similar plot of `districts_RGF93`.
* Calculate the area of all districts again with `districts_RGF93` (the result will now be expressed in m²).
    
    
<details><summary>Hints</summary>

* The CRS information is stored in the `.crs` attribute of a GeoDataFrame.
* Making a simple plot of a GeoDataFrame can be done with the `.plot()` method.
* Converting to a different CRS can be done with the `.to_crs()` method, and the CRS can be specified as an EPSG number using the `epsg` keyword.

</details>

</div>

```{code-cell} ipython3
:clear_cell: true

# Import the districts dataset
districts = geopandas.read_file("data/paris_districts.geojson")
```

```{code-cell} ipython3
:clear_cell: true

# Check the CRS information
districts.crs
```

```{code-cell} ipython3
:clear_cell: true

# Show the first rows of the GeoDataFrame
districts.head()
```

```{code-cell} ipython3
:clear_cell: true

# Plot the districts dataset
districts.plot()
```

```{code-cell} ipython3
:clear_cell: true

# Calculate the area of all districts
districts.geometry.area
```

```{code-cell} ipython3
:clear_cell: true

# Convert the districts to the RGF93 reference system
districts_RGF93 = districts.to_crs(epsg=2154)  # or to_crs("EPSG:2154")
```

```{code-cell} ipython3
:clear_cell: true

# Plot the districts dataset again
districts_RGF93.plot()
```

```{code-cell} ipython3
:clear_cell: true

# Calculate the area of all districts (the result is now expressed in m²)
districts_RGF93.geometry.area
```

<div class="alert alert-success">

**EXERCISE:**

In the previous notebook, we did an exercise on plotting the bike stations locations in Paris and adding a background map to it using the `contextily` package.

Currently, `contextily` assumes that your data is in the Web Mercator projection, the system used by most web tile services. And in that first exercise, we provided the data in the appropriate CRS so you didn't need to care about this aspect.

However, typically, your data will not come in Web Mercator (`EPSG:3857`) and you will have to align them with web tiles on your own.
    
* Read the bike stations datasets (`"data/paris_bike_stations.geojson"`) into a GeoDataFrame called `stations`.
* Convert the `stations` dataset to the Web Mercator projection (`EPSG:3857`). Call the result `stations_webmercator`, and inspect the result.
* Make a plot of this projected dataset (specify the marker size to be 5) and add a background map using `contextily`.

    
<details><summary>Hints</summary>

* Making a simple plot of a GeoDataFrame can be done with the `.plot()` method. This returns a matplotlib axes object.
* The marker size can be specified with the `markersize` keyword if the `.plot()` method.
* To add a background map, use the `contextily.add_basemap()` function. It takes the matplotlib `ax` to which to add a map as the first argument.

</details>

</div>

```{code-cell} ipython3
:clear_cell: true

stations = geopandas.read_file("data/paris_bike_stations.geojson")
stations.head()
```

```{code-cell} ipython3
:clear_cell: true

# Convert to the Web Mercator projection
stations_webmercator = stations.to_crs("EPSG:3857")
stations.head()
```

```{code-cell} ipython3
:clear_cell: true

# Plot the stations with a background map
import contextily
ax = stations_webmercator.plot(markersize=5)
contextily.add_basemap(ax)
```
