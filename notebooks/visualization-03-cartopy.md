---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.0
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

<p><font size="6"><b>Creating maps with Cartopy</b></font></p>


> *DS Python for GIS and Geoscience*  
> *October, 2021*
>
> *© 2021, Joris Van den Bossche and Stijn Van Hoey. Licensed under [CC BY-SA 4.0 Creative Commons](https://creativecommons.org/licenses/by-sa/4.0/)* Adapted from material from Phil Elson and Ryan Abernathey (see below).

---

# Maps in Scientific Python

Making maps is a fundamental part of GIS and geoscience research.
Maps differ from regular figures in the following principle ways:

- Maps require a *projection* of geographic coordinates on the 3D Earth to the 2D space of your figure.
- Maps often include extra decorations besides just our data (e.g. continents, country borders, etc.)

The maps we have made up to now, for example using the GeoPandas `plot()` method, assume the data can be plotted as is on the figure. This works fine if your data is already in projected coordinates, and has a limited extent (small study area). When mapping data of a larger area of the full globe, properly taking into account the projection becomes much more important!

In this notebook, we will learn about [Cartopy](https://scitools.org.uk/cartopy/docs/latest/), one of the most common packages for making maps within python.

### Credit: Phil Elson and Ryan Abernathey

Lots of the material in this notebook was adopted from https://earth-env-data-science.github.io/intro.html by Ryan Abernathey, which itself was adopted from [Phil Elson](https://pelson.github.io/)'s excellent [Cartopy Tutorial](https://github.com/SciTools/cartopy-tutorial). Phil is the creator of Cartopy and published his tutorial under an [open license](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/), meaning that we can copy, adapt, and redistribute it as long as we give proper attribution. **THANKS PHIL AND RYAN!** 👏👏👏

+++

## Background: Projections

+++

### Most of our media for visualization *are* flat

Our two most common media are flat:

 * Paper
 * Screen

![](https://raw.githubusercontent.com/SciTools/cartopy-tutorial/master/static/flat_medium.jpg)

### [Map] Projections: Taking us from spherical to flat

A map projection (or more commonly refered to as just "projection") is:

> a systematic transformation of the latitudes and longitudes of locations from the surface of a sphere or an ellipsoid into locations on a plane. [[Wikipedia: Map projection](https://en.wikipedia.org/wiki/Map_projection)].

### The major problem with map projections

![orange peel](https://raw.githubusercontent.com/SciTools/cartopy-tutorial/master/static/orange_peel.jpg)

 * The surface of a sphere is topologically different to a 2D surface, therefore we *have* to cut the sphere *somewhere*
 * A sphere's surface cannot be represented on a plane without distortion.
 
There are many different ways to make a projection, and we will not attempt to explain all of the choices and tradeoffs here. Instead, you can read Phil's [original tutorial](https://github.com/SciTools/cartopy-tutorial/blob/master/tutorial/projections_crs_and_terms.ipynb) for a great overview of this topic.
Instead, we will dive into the more practical sides of Caropy usage.

+++

## Introducing Cartopy

https://scitools.org.uk/cartopy/docs/latest/

Cartopy makes use of the powerful [PROJ.4](https://proj4.org/), numpy and shapely libraries and includes a programatic interface built on top of Matplotlib for the creation of publication quality maps.

Key features of cartopy are its object oriented projection definitions, and its ability to transform points, lines, vectors, polygons and images between those projections.

### Cartopy Projections and other reference systems

In Cartopy, each projection is a class.
Most classes of projection can be configured in projection-specific ways, although Cartopy takes an opinionated stance on sensible defaults.

Let's create a Plate Carree projection instance.

To do so, we need cartopy's crs module. This is typically imported as ``ccrs`` (Cartopy Coordinate Reference Systems).

```{code-cell} ipython3
import cartopy.crs as ccrs
import cartopy
```

Cartopy's projection list tells us that the Plate Carree projection is available with the ``ccrs.PlateCarree`` class: https://scitools.org.uk/cartopy/docs/latest/crs/projections.html

**Note:** we need to *instantiate* the class in order to do anything projection-y with it!

```{code-cell} ipython3
ccrs.PlateCarree()
```

### Drawing a map

Cartopy optionally depends upon matplotlib, and each projection knows how to create a matplotlib Axes (or AxesSubplot) that can represent itself.

The Axes that the projection creates is a [cartopy.mpl.geoaxes.GeoAxes](https://scitools.org.uk/cartopy/docs/latest/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes). This Axes subclass overrides some of matplotlib's existing methods, and adds a number of extremely useful ones for drawing maps:

```{code-cell} ipython3
import matplotlib.pyplot as plt

fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
ax
```

That was a little underwhelming, but we can see that the Axes created is indeed one of those GeoAxes[Subplot] instances.

One of the most useful methods that this class adds on top of the standard matplotlib Axes class is the ``coastlines`` method. With no arguments, it will add the Natural Earth ``1:110,000,000`` scale coastline data to the map.

```{code-cell} ipython3
fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
ax.coastlines()
```

Projection classes have options we can use to customize the map

```{code-cell} ipython3
ccrs.PlateCarree?
```

```{code-cell} ipython3
fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)})
ax.coastlines()
```

### Useful methods of a GeoAxes

The [cartopy.mpl.geoaxes.GeoAxes](https://scitools.org.uk/cartopy/docs/latest/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes) class adds a number of useful methods.

Let's take a look at:

 * [set_global](https://scitools.org.uk/cartopy/docs/latest/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes.set_global) - zoom the map out as much as possible
 * [set_extent](https://scitools.org.uk/cartopy/docs/latest/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes.set_extent) - zoom the map to the given bounding box
 

 * [gridlines](https://scitools.org.uk/cartopy/docs/latest/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes.graticule) - add a graticule (and optionally labels) to the axes
 * [coastlines](https://scitools.org.uk/cartopy/docs/latest/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes.coastlines) - add Natural Earth coastlines to the axes
 * [stock_img](https://scitools.org.uk/cartopy/docs/latest/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes.stock_img) - add a low-resolution Natural Earth background image to the axes
 
 
 * [imshow](https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.imshow.html#matplotlib.axes.Axes.imshow) - add an image (numpy array) to the axes
 * [add_geometries](https://scitools.org.uk/cartopy/docs/latest/matplotlib/geoaxes.html#cartopy.mpl.geoaxes.GeoAxes.add_geometries) - add a collection of geometries (Shapely / GeoPandas) to the axes
 
### Some More Examples of Different Global Projections

```{code-cell} ipython3
projections = [ccrs.PlateCarree(),
               ccrs.Robinson(),
               ccrs.Mercator(),
               ccrs.Orthographic(),
               ccrs.InterruptedGoodeHomolosine()
              ]


for proj in projections:
    fig, ax = plt.subplots(subplot_kw={'projection': proj})
    ax.stock_img()
    ax.coastlines()
    ax.set_title(f'{type(proj)}')
```

### Regional Maps

To create a regional map, we use the `set_extent` method of GeoAxis to limit the size of the region.

```{code-cell} ipython3
ax.set_extent?
```

```{code-cell} ipython3
central_lon, central_lat = -10, 45
extent = [-40, 20, 30, 60]
fig, ax = plt.subplots(subplot_kw={'projection': ccrs.Orthographic(central_lon, central_lat)})
ax.set_extent(extent)
ax.gridlines()
ax.coastlines(resolution='50m')
```

## Adding features to the map

To give our map more styles and details, we add `cartopy.feature` objects.
Many useful features are built in. These "default features" are at coarse (110m) resolution.

Name | Description
-----|------------
`cartopy.feature.BORDERS` | Country boundaries
`cartopy.feature.COASTLINE` | Coastline, including major islands
`cartopy.feature.LAKES` | Natural and artificial lakes
`cartopy.feature.LAND` | Land polygons, including major islands
`cartopy.feature.OCEAN` | Ocean polygons
`cartopy.feature.RIVERS` | Single-line drainages, including lake centerlines
`cartopy.feature.STATES` | (limited to the United States at this scale)

Below we illustrate these features in a customized map of North America.

```{code-cell} ipython3
import cartopy.feature as cfeature
import numpy as np

central_lat = 37.5
central_lon = -96
extent = [-120, -70, 24, 50.5]
central_lon = np.mean(extent[:2])
central_lat = np.mean(extent[2:])

plt.figure(figsize=(12, 6))
ax = plt.axes(projection=ccrs.AlbersEqualArea(central_lon, central_lat))
ax.set_extent(extent)

ax.add_feature(cartopy.feature.OCEAN)
ax.add_feature(cartopy.feature.LAND, edgecolor='black')
ax.add_feature(cartopy.feature.LAKES, edgecolor='black')
ax.add_feature(cartopy.feature.RIVERS)
ax.gridlines()
```

If we want higher-resolution features, Cartopy can automatically download and create them from the [Natural Earth Data](http://www.naturalearthdata.com/) database or the [GSHHS dataset](https://www.ngdc.noaa.gov/mgg/shorelines/gshhs.html) database.

+++

## Adding vector data to the map

You will typically have your own data to add to a map, of course. To add vector data, we can add single Shapely geometries with `ax.add_geometries()`, or combine with GeoPandas.

The GeoPandas `plot()` method works *if*:

* you pass the GeoAxes object to the `ax=` keyword
* the data is in the same CRS as the cartopy projection OR you specify the corresponding `transform=` in the `plot()` method.

```{code-cell} ipython3
import geopandas
cities = geopandas.read_file("zip://./data/ne_110m_populated_places.zip")
```

```{code-cell} ipython3
proj = ccrs.AlbersEqualArea()

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': proj})
# Reproject the cities dataset to the corresponding CRS of the cartopy projection
cities_albers = cities.to_crs(proj.proj4_init)
cities_albers.plot(ax=ax)
ax.coastlines()
ax.set_global()
ax.gridlines(draw_labels=True)
```

```{code-cell} ipython3
proj = ccrs.AlbersEqualArea()

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': proj})
# cities is in geographic lat/lon data, so we can specify PlateCarree as the cartopy equivalent
cities.plot(ax=ax, transform=ccrs.PlateCarree())
ax.coastlines()
ax.set_global()
ax.gridlines(draw_labels=True)
```

Or we can also plot specific points:

```{code-cell} ipython3
proj = ccrs.AlbersEqualArea()

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': proj})
ax.plot(0, 0, marker='o', color='red', markersize=12, transform=ccrs.PlateCarree())
ax.coastlines()
ax.set_global()
ax.gridlines()
```

Because our map is a matplotlib axis, we can use all the familiar maptplotlib commands to make plots.
By default, the map extent will be adjusted to match the data. We can override this with the `.set_global` or `.set_extent` commands.

Another example to show the difference of adding a transform or not:

```{code-cell} ipython3
# create some test data
new_york = dict(lon=-74.0060, lat=40.7128)
honolulu = dict(lon=-157.8583, lat=21.3069)
lons = [new_york['lon'], honolulu['lon']]
lats = [new_york['lat'], honolulu['lat']]
```

Key point: **the data also have to be transformed to the projection space**.
This is done via the `transform=` keyword in the plotting method. The argument is another `cartopy.crs` object.
If you don't specify a transform, Cartopy assume that the data is using the same projection as the underlying GeoAxis.

From the [Cartopy Documentation](https://scitools.org.uk/cartopy/docs/latest/tutorials/understanding_transform.html)

> The core concept is that the projection of your axes is independent of the coordinate system your data is defined in. The `projection` argument is used when creating plots and determines the projection of the resulting plot (i.e. what the plot looks like). The `transform` argument to plotting functions tells Cartopy what coordinate system your data are defined in.

```{code-cell} ipython3
fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
ax.plot(lons, lats, label='Equirectangular straight line')
ax.plot(lons, lats, label='Great Circle', transform=ccrs.Geodetic())
ax.coastlines()
ax.legend()
ax.set_global()
```

## Adding raster data to the map

The same principles apply to 2D data. Below we create some example data defined in regular lat / lon coordinates.

```{code-cell} ipython3
import numpy as np
lon = np.linspace(-80, 80, 25)
lat = np.linspace(30, 70, 25)
lon2d, lat2d = np.meshgrid(lon, lat)
data = np.cos(np.deg2rad(lat2d) * 4) + np.sin(np.deg2rad(lon2d) * 4)
plt.contourf(lon2d, lat2d, data)
```

Now we create a `PlateCarree` projection and plot the data on it without any `transform` keyword.
This happens to work because `PlateCarree` is the simplest projection of lat / lon data.

```{code-cell} ipython3
fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
ax.set_global()
ax.coastlines()
ax.contourf(lon, lat, data)
```

However, if we try the same thing with a different projection, we get the wrong result.

```{code-cell} ipython3
projection = ccrs.RotatedPole(pole_longitude=-177.5, pole_latitude=37.5)
fig, ax = plt.subplots(subplot_kw={'projection': projection})
ax.set_global()
ax.coastlines()
ax.contourf(lon, lat, data)
```

To fix this, we need to pass the correct transform argument to `contourf`:

```{code-cell} ipython3
projection = ccrs.RotatedPole(pole_longitude=-177.5, pole_latitude=37.5)
fig, ax = plt.subplots(subplot_kw={'projection': projection})
ax.set_global()
ax.coastlines()
ax.contourf(lon, lat, data, transform=ccrs.PlateCarree())
```

### Showing Images

We can plot a satellite image easily on a map if we know its extent

```{code-cell} ipython3
! wget https://github.com/mapbox/rasterio/raw/master/tests/data/RGB.byte.tif
```

```{code-cell} ipython3
import rasterio
import rasterio.plot
```

```{code-cell} ipython3
with rasterio.open('RGB.byte.tif') as src:
    img_extent = rasterio.plot.plotting_extent(src)
    img = src.read()
    print(src.meta)

img = rasterio.plot.reshape_as_image(img)
```

```{code-cell} ipython3
proj = ccrs.UTM(zone=18, southern_hemisphere=False)
```

```{code-cell} ipython3
proj
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(8, 12), subplot_kw={'projection': proj})

ax.imshow(img, extent=img_extent, transform=proj)
ax.coastlines(resolution='10m', color='red', linewidth=1)
```

## Xarray Integration

Cartopy transforms can be passed to xarray! This creates a very quick path for creating professional looking maps from netCDF data.

```{code-cell} ipython3
import xarray as xr
url = 'http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/noaa.ersst.v5/sst.mnmean.nc'
ds = xr.open_dataset(url, drop_variables=['time_bnds'])
ds
```

```{code-cell} ipython3
sst = ds.sst.sel(time='2000-01-01', method='nearest')
fig = plt.figure(figsize=(9,6))
ax = plt.axes(projection=ccrs.Robinson())
ax.coastlines()
ax.gridlines()
sst.plot(ax=ax, transform=ccrs.PlateCarree(),
         vmin=2, vmax=30, cbar_kwargs={'shrink': 0.4})
```

## Add OGC WMS and WMTS services to cartopy

+++

A lot of online map services are available, which are capable of providing background layers to a map similar as these are used in online applications. The [OGC WMS/WMTS](https://www.ogc.org/standards/wms) (Web Map Service) are important standards by which a lot of map layers are made available.

A (non-official, but very comprehensive) list of such services for Belgium is made available by Michel Stuyts, see https://wms.michelstuyts.be. It is always a matter of finding the correct URL and the `layer_name` for a given service.

As an example, consider the Orthophoto WMS (provided by the National Geographic Institute):

- WMS: https://wms.ngi.be/inspire/ortho/service
- GetCapabilities: https://wms.ngi.be/inspire/ortho/service?REQUEST=GetCapabilities&SERVICE=WMS

With the following layers available (see website Stuyts or GetCapabilities overview):

- orthoimage_coverage: Orthoimage coverage
- orthoimage_coverage_2016: Orthoimage coverage - 2016
- orthoimage_coverage_2018: Orthoimage coverage - 2018

Let's use the `orthoimage_coverage` incombination with our city of Ghent contours data set:

```{code-cell} ipython3
base_uri = 'https://wms.ngi.be/inspire/ortho/service'
layer_name = 'orthoimage_coverage'

plain_crs = ccrs.Mercator()
fig, ax = plt.subplots(subplot_kw={"projection": plain_crs}, figsize=(10, 10))
ax.set_extent([3.57, 3.85, 50.98, 51.19], crs=ccrs.PlateCarree())

# Add WMS imaging.
ax.add_wms(base_uri, layers=layer_name)

# Add city of Ghent boundary from file
gent = geopandas.read_file("./data/gent/vector/gent.geojson")
gent = gent.to_crs(plain_crs.proj4_init)  # adjust to projection
gent.plot(ax=ax, facecolor="none", edgecolor="white", linewidth=2)
```

Someone interested in flood control, might want to know the sensitive areas for inundation in this area. Looking in the available services, https://inspirepub.waterinfo.be/arcgis/rest/services/overstroombaargebied/MapServer/WMTS/1.0.0/WMTSCapabilities.xml has the available layer `overstroombaargebied: overstroombaargebied` (dutch for inundation sensitive area).

Hence, we can combine this WMTS layer into the map as well:

```{code-cell} ipython3
plain_crs = ccrs.Mercator()
fig, ax = plt.subplots(subplot_kw={"projection": plain_crs}, figsize=(10, 10))
ax.set_extent([3.57, 3.85, 50.98, 51.19], crs=ccrs.PlateCarree())

# Add WMS imaging of ortophoto.
base_uri = 'https://wms.ngi.be/inspire/ortho/service'
layer_name = 'orthoimage_coverage'
ax.add_wms(base_uri, layers=layer_name)

# Add WMTS of sensitive areas for inundation.
base_uri = 'https://inspirepub.waterinfo.be/arcgis/rest/services/archief/Overstromingsgevoelige_gebieden_2006/MapServer/WMTS'
layer_name = 'archief_Overstromingsgevoelige_gebieden_2006'
ax.add_wmts(base_uri, layer_name=layer_name, alpha=0.8)

# Add city of Ghent boundary from file
gent = geopandas.read_file("./data/gent/vector/gent.geojson")
gent = gent.to_crs(plain_crs.proj4_init)  # adjust to projection
gent.plot(ax=ax, facecolor="none", edgecolor="#433d78", linewidth=2)
```

## Doing More

Browse the [Cartopy Gallery](https://scitools.org.uk/cartopy/docs/latest/gallery/index.html) to learn about all the different types of data and plotting methods available!

```{code-cell} ipython3

```
