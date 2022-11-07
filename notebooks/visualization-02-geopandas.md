---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.0
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

<p><font size="6"><b> Visualizing spatial data with Python: GeoPandas</b></font></p>


> *DS Python for GIS and Geoscience*  
> *October, 2022*
>
> *© 2022, Joris Van den Bossche and Stijn Van Hoey. Licensed under [CC BY 4.0 Creative Commons](https://creativecommons.org/licenses/by/4.0/)*

---

```{code-cell} ipython3
%matplotlib inline

import pandas as pd
import geopandas

import matplotlib.pyplot as plt
```

```{code-cell} ipython3
countries = geopandas.read_file("zip://./data/ne_110m_admin_0_countries.zip")
countries = countries[countries['continent'] != "Antarctica"]
cities = geopandas.read_file("zip://./data/ne_110m_populated_places.zip")
rivers = geopandas.read_file("zip://./data/ne_50m_rivers_lake_centerlines.zip")
```

## GeoPandas visualization functionality

+++

GeoPandas itself provides some visualization functionality, and together with matplotlib for further customization, you can already get decent results for visualizing vector data.

+++

#### Basic plot

```{code-cell} ipython3
countries.plot()
```

#### Adjusting the figure size

```{code-cell} ipython3
countries.plot(figsize=(15, 6))
```

#### Removing the box / x and y coordinate labels

```{code-cell} ipython3
ax = countries.plot(figsize=(15, 6))
ax.set_axis_off()
```

#### Coloring based on column values

Let's first create a new column with the GDP per capita:

```{code-cell} ipython3
countries = countries[(countries['pop_est'] >0 ) & (countries['name'] != "Antarctica")]
```

```{code-cell} ipython3
countries['gdp_per_cap'] = countries['gdp_md_est'] / countries['pop_est'] * 100
```

and now we can use this column to color the polygons:

```{code-cell} ipython3
ax = countries.plot(figsize=(15, 6), column='gdp_per_cap', legend=True)
ax.set_axis_off()
```

Using a classification scheme to bin the values (using [`mapclassify`](https://pysal.org/mapclassify/)):

```{code-cell} ipython3
ax = countries.plot(figsize=(15, 6), column='gdp_per_cap', scheme='quantiles', legend=True)
ax.set_axis_off()
```

#### Combining different dataframes on a single plot

The `.plot` method returns a matplotlib Axes object, which can then be re-used to add additional layers to that plot with the `ax=` keyword:

```{code-cell} ipython3
ax = countries.plot(figsize=(15, 6))
cities.plot(ax=ax, color='red', markersize=10)
ax.set_axis_off()
```

```{code-cell} ipython3
ax = countries.plot(edgecolor='k', facecolor='none', figsize=(8, 8))
rivers.plot(ax=ax)
cities.plot(ax=ax, color='C1')
ax.set(xlim=(-20, 60), ylim=(-40, 40))
```

## Adding a background map with contextily

+++

The contextily package allow to easily add a web-tile based background (basemap) to your GeoPandas plots.

Currently, the only requirement is that your data is already in the WebMercator projection (EPSG:3857).

```{code-cell} ipython3
# selecting the cities in Europe
cities_europe = cities[cities.within(countries[countries['continent'] == 'Europe'].unary_union)]
```

```{code-cell} ipython3
# converting to WebMercator
cities_europe2 = cities_europe.to_crs(epsg=3857)
```

```{code-cell} ipython3
ax = cities_europe2.plot()
```

```{code-cell} ipython3
import contextily
```

```{code-cell} ipython3
# import matplotlib
# matplotlib.rcParams['figure.dpi'] = 300
```

```{code-cell} ipython3
ax = cities_europe2.plot(figsize=(10, 6))
contextily.add_basemap(ax)
```

```{code-cell} ipython3
ax = cities_europe2.plot(figsize=(10, 6))
contextily.add_basemap(ax, source=contextily.providers.Stamen.TonerLite)
```

## Projection-aware maps with Cartopy

Cartopy is the base matplotlib cartographic library, and it is used by `geoplot` under the hood to provide projection-awareness (http://scitools.org.uk/cartopy/docs/latest/index.html).

The following example is taken from the docs: http://geopandas.readthedocs.io/en/latest/gallery/cartopy_convert.html#sphx-glr-gallery-cartopy-convert-py

```{code-cell} ipython3
from cartopy import crs as ccrs
```

```{code-cell} ipython3
# Define the CartoPy CRS object.
crs = ccrs.AlbersEqualArea()

# This can be converted into a `proj4` string/dict compatible with GeoPandas
crs_proj4 = crs.proj4_init
countries_ae = countries.to_crs(crs_proj4)
```

```{code-cell} ipython3
# Here's what the plot looks like in GeoPandas
countries_ae.plot()
```

```{code-cell} ipython3
# Here's what the plot looks like when plotting with cartopy
fig, ax = plt.subplots(subplot_kw={'projection': crs})
ax.add_geometries(countries_ae['geometry'], crs=crs)
```

```{code-cell} ipython3
# Here's what the plot looks like when plotting with cartopy and geopandas combined
fig, ax = plt.subplots(subplot_kw={'projection': crs})
countries_ae['geometry'].plot(ax=ax)
ax.set_global()
ax.gridlines()
```

**For more on cartopy**, see the [visualization-03-cartopy.ipynb](visualization-03-cartopy.ipynb) notebook.

+++

## Using `geoplot`

The `geoplot` packages provides some additional functionality compared to the basic `.plot()` method on GeoDataFrames:

- High-level plotting API (with more plot types as geopandas)
- Native projection support through cartopy

https://residentmario.github.io/geoplot/index.html

```{code-cell} ipython3
import geoplot
import geoplot.crs as gcrs
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={
    'projection': gcrs.Orthographic(central_latitude=40.7128, central_longitude=-74.0059)
})
geoplot.choropleth(countries, hue='gdp_per_cap', projection=gcrs.Orthographic(), ax=ax,
                   cmap='magma', linewidth=0.5, edgecolor='white')
ax.set_global()
ax.spines['geo'].set_visible(True)
```

## Interactive web-based visualizations

There are nowadays many libraries that target interactive web-based visualizations and that can handle geospatial data. Some packages with an example for each:

- Bokeh: https://bokeh.pydata.org/en/latest/docs/gallery/texas.html
- GeoViews (other interface to Bokeh/matplotlib): http://geo.holoviews.org
- Altair: https://altair-viz.github.io/gallery/choropleth.html
- Plotly: https://plot.ly/python/#maps
- ...

+++

Another popular javascript library for online maps is [Leaflet.js](https://leafletjs.com/), and this has python bindings in the [folium](https://github.com/python-visualization/folium) and [ipyleaflet](https://github.com/jupyter-widgets/ipyleaflet) packages.

+++

An example with ipyleaflet:

```{code-cell} ipython3
import ipyleaflet
```

```{code-cell} ipython3
m = ipyleaflet.Map(center=[48.8566, 2.3429], zoom=6)

layer = ipyleaflet.GeoJSON(data=cities.__geo_interface__)
m.add_layer(layer)
m
```

```{code-cell} ipython3
m = ipyleaflet.Map(center=[48.8566, 2.3429], zoom=3)
geo_data = ipyleaflet.GeoData(
    geo_dataframe = countries,
    style={'color': 'black', 'fillColor': '#3366cc', 'opacity':0.05, 'weight':1.9, 'dashArray':'2', 'fillOpacity':0.6},
    hover_style={'fillColor': 'red' , 'fillOpacity': 0.2},
    name = 'Countries')
m.add_layer(geo_data)
m
```

More: https://ipyleaflet.readthedocs.io/en/latest/api_reference/geodata.html

+++

An example with folium:

```{code-cell} ipython3
import folium
```

```{code-cell} ipython3
m = folium.Map([48.8566, 2.3429], zoom_start=6, tiles="OpenStreetMap")
folium.GeoJson(countries).add_to(m)
folium.GeoJson(cities).add_to(m)
m
```

```{code-cell} ipython3
m = folium.Map([0, 0], zoom_start=1)
folium.Choropleth(geo_data=countries, data=countries, columns=['iso_a3', 'gdp_per_cap'],
             key_on='feature.properties.iso_a3', fill_color='BuGn', highlight=True).add_to(m)
m
```

### In the upcoming GeoPandas release: a default interactive `explore()` method (based on Folium)

Currently this lives at https://github.com/martinfleis/geopandas-view/, but it will be integrated in the next release of GeoPandas:

```{code-cell} ipython3
from geopandas_view import view as explore
```

```{code-cell} ipython3
explore(countries)
```
