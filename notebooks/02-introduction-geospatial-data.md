---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

<p><font size="6"><b> Introduction to geospatial vector data in Python</b></font></p>


> *DS Python for GIS and Geoscience*  
> *September, 2024*
>
> *© 2024, Joris Van den Bossche and Stijn Van Hoey  (<mailto:jorisvandenbossche@gmail.com>, <mailto:stijnvanhoey@gmail.com>). Licensed under [CC BY 4.0 Creative Commons](http://creativecommons.org/licenses/by/4.0/)*

---

```{code-cell} ipython3
%matplotlib inline

import pandas as pd
import geopandas
```

## Importing geospatial data

+++

Geospatial data is often available from specific GIS file formats or data stores, like ESRI shapefiles, GeoJSON files, geopackage files, PostGIS (PostgreSQL) database, ...

We can use the GeoPandas library to read many of those GIS file formats (relying on the `fiona` library under the hood, which is an interface to GDAL/OGR), using the `geopandas.read_file` function.

For example, let's start by reading a shapefile with all the countries of the world (adapted from http://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/, zip file is available in the `/data` directory), and inspect the data:

```{code-cell} ipython3
countries = geopandas.read_file("data/ne_110m_admin_0_countries.zip")
# or if the archive is unpacked:
# countries = geopandas.read_file("data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")
```

```{code-cell} ipython3
countries.head()
```

```{code-cell} ipython3
countries.plot()
```

```{code-cell} ipython3
countries.explore()
```

What do we observe:

- Using `.head()` we can see the first rows of the dataset, just like we can do with Pandas.
- There is a `geometry` column and the different countries are represented as polygons
- We can use the `.plot()` (matplotlib) or `explore()` (Folium / Leaflet.js) method to quickly get a *basic* visualization of the data

+++

## What's a GeoDataFrame?

We used the GeoPandas library to read in the geospatial data, and this returned us a `GeoDataFrame`:

```{code-cell} ipython3
type(countries)
```

A GeoDataFrame contains a tabular, geospatial dataset:

* It has a **'geometry' column** that holds the geometry information (or features in GeoJSON).
* The other columns are the **attributes** (or properties in GeoJSON) that describe each of the geometries

Such a `GeoDataFrame` is just like a pandas `DataFrame`, but with some additional functionality for working with geospatial data:

* A `.geometry` attribute that always returns the column with the geometry information (returning a GeoSeries). The column name itself does not necessarily need to be 'geometry', but it will always be accessible as the `.geometry` attribute.
* It has some extra methods for working with spatial data (area, distance, buffer, intersection, ...), which we will learn in later notebooks

```{code-cell} ipython3
countries.geometry
```

```{code-cell} ipython3
type(countries.geometry)
```

```{code-cell} ipython3
countries.geometry.area
```

**It's still a DataFrame**, so we have all the Pandas functionality available to use on the geospatial dataset, and to do data manipulations with the attributes and geometry information together.

For example, we can calculate average population number over all countries (by accessing the 'pop_est' column, and calling the `mean` method on it):

```{code-cell} ipython3
countries['pop_est'].mean()
```

Or, we can use boolean filtering to select a subset of the dataframe based on a condition:

```{code-cell} ipython3
africa = countries[countries['continent'] == 'Africa']
```

```{code-cell} ipython3
africa.plot();
```

<div class="alert alert-info" style="font-size:120%">

**REMEMBER:** <br>

* A `GeoDataFrame` allows to perform typical tabular data analysis together with spatial operations
* A `GeoDataFrame` (or *Feature Collection*) consists of:
    * **Geometries** or **features**: the spatial objects
    * **Attributes** or **properties**: columns with information about each spatial object

</div>

+++

## Geometries: Points, Linestrings and Polygons

Spatial **vector** data can consist of different types, and the 3 fundamental types are:

![](../img/simple_features_3_text.svg)

* **Point** data: represents a single point in space.
* **Line** data ("LineString"): represents a sequence of points that form a line.
* **Polygon** data: represents a filled area.

And each of them can also be combined in multi-part geometries (See https://shapely.readthedocs.io/en/stable/manual.html#geometric-objects for extensive overview).

+++

For the example we have seen up to now, the individual geometry objects are Polygons:

```{code-cell} ipython3
print(countries.geometry[2])
```

Let's import some other datasets with different types of geometry objects.

A dateset about cities in the world (adapted from http://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-populated-places/, zip file is available in the `/data` directory), consisting of Point data:

```{code-cell} ipython3
cities = geopandas.read_file("data/ne_110m_populated_places.zip")
```

```{code-cell} ipython3
print(cities.geometry[0])
```

And a dataset of rivers in the world (from http://www.naturalearthdata.com/downloads/50m-physical-vectors/50m-rivers-lake-centerlines/, zip file is available in the `/data` directory) where each river is a (multi-)line:

```{code-cell} ipython3
rivers = geopandas.read_file("data/ne_50m_rivers_lake_centerlines.zip")
```

```{code-cell} ipython3
print(rivers.geometry[0])
```

### The `shapely` library

The individual geometry objects are provided by the [`shapely`](https://shapely.readthedocs.io/en/stable/) library

```{code-cell} ipython3
type(countries.geometry[0])
```

To construct one ourselves:

```{code-cell} ipython3
from shapely import Point, Polygon, LineString
```

```{code-cell} ipython3
p = Point(0, 0)
```

```{code-cell} ipython3
print(p)
```

```{code-cell} ipython3
polygon = Polygon([(1, 1), (2,2), (2, 1)])
```

```{code-cell} ipython3
polygon.area
```

```{code-cell} ipython3
polygon.distance(p)
```

<div class="alert alert-info" style="font-size:120%">

**REMEMBER**: <br>

Single geometries are represented by `shapely` objects:

* If you access a single geometry of a GeoDataFrame, you get a shapely geometry object
* Those objects have similar functionality as geopandas objects (GeoDataFrame/GeoSeries). For example:
    * `single_shapely_object.distance(other_point)` -> distance between two points
    * `geodataframe.distance(other_point)` ->  distance for each point in the geodataframe to the other point

</div>

+++

## Plotting our different layers together

```{code-cell} ipython3
# import matplotlib.pyplot as plt
# fig, ax = plt.subplots(figsize=(10, 8))
ax = countries.plot(edgecolor='k', facecolor='none', figsize=(10, 8))
rivers.plot(ax=ax)
cities.plot(ax=ax, color='red')
ax.set(xlim=(-20, 60), ylim=(-40, 40))
```

See the [visualization-02-geopandas.ipynb](visualization-02-geopandas.ipynb) notebook for more details on visualizing geospatial datasets.

+++

## Let's practice!

Throughout the exercises in this course, we will work with several datasets about the city of Paris.

Here, we start with the following datasets:

- The administrative districts of Paris (https://opendata.paris.fr/explore/dataset/quartier_paris/): `paris_districts_utm.geojson`
- Real-time (at the moment I downloaded them ..) information about the public bicycle sharing system in Paris (vélib, https://opendata.paris.fr/explore/dataset/stations-velib-disponibilites-en-temps-reel/information/): `data/paris_bike_stations_mercator.gpkg`

Both datasets are provided as spatial datasets using a GIS file format.

Let's explore further those datasets, now using the spatial aspect as well.

+++

<div class="alert alert-success">

**EXERCISE**:

We will start with exploring the bicycle station dataset (available as a GeoPackage file: `data/paris_bike_stations_mercator.gpkg`)
    
* Read the stations datasets into a GeoDataFrame called `stations`.
* Check the type of the returned object
* Check the first rows of the dataframes. What kind of geometries does this datasets contain?
* How many features are there in the dataset? 
    
<details><summary>Hints</summary>

* Use `type(..)` to check any Python object type
* The `geopandas.read_file()` function can read different geospatial file formats. You pass the file name as first argument.
* Use the `.shape` attribute to get the number of features

</details>
    
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

stations = geopandas.read_file("data/paris_bike_stations_mercator.gpkg")
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

type(stations)
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

stations.head()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

stations.shape
```

<div class="alert alert-success">

**EXERCISE**:

* Make a quick plot of the `stations` dataset.
* Make the plot a bit larger by setting the figure size to (12, 6) (hint: the `plot` method accepts a `figsize` keyword).
 
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

stations.plot(figsize=(12,6))  # or .explore()
```

A plot with just some points can be hard to interpret without any spatial context. We have seen that we can use the `explore()` method to easily get an interactive figure that by default includes a background map. But also for the static matplotlib-based plot, it can be useful to add such a base map, and that's what we will learn in the next excercise.

We are going to make use of the [contextily](https://github.com/darribas/contextily) package. The `add_basemap()` function of this package makes it easy to add a background web map to our plot. We begin by plotting our data first, and then pass the matplotlib axes object (returned by dataframe's `plot()` method) to the `add_basemap()` function. `contextily` will then download the web tiles needed for the geographical extent of your plot.


<div class="alert alert-success">

**EXERCISE**:

* Import `contextily`.
* Re-do the figure of the previous exercise: make a plot of all the points in `stations`, but assign the result to an `ax` variable.
* Set the marker size equal to 5 to reduce the size of the points (use the `markersize` keyword of the `plot()` method for this).
* Use the `add_basemap()` function of `contextily` to add a background map: the first argument is the matplotlib axes object `ax`.

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

import contextily
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

ax = stations.plot(figsize=(12,6), markersize=5)
contextily.add_basemap(ax)
```

<div class="alert alert-success">

**EXERCISE**:

* Make a histogram showing the distribution of the number of bike stands in the stations.

<details>
  <summary>Hints</summary>

* Selecting a column can be done with the square brackets: `df['col_name']`
* Single columns have a `hist()` method to plot a histogram of its values.
    
</details>
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

stations['bike_stands'].plot.hist()
```

<div class="alert alert-success">

**EXERCISE**:

Let's now visualize where the available bikes are actually stationed:
    
* Make a plot of the `stations` dataset (also with a (12, 6) figsize).
* Use the `'available_bikes'` columns to determine the color of the points. For this, use the `column=` keyword.
* Use the `legend=True` keyword to show a color bar.
 
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

stations.plot(figsize=(12, 6), column='available_bikes', legend=True)
```

<div class="alert alert-success">

**EXERCISE**:

Next, we will explore the dataset on the administrative districts of Paris (available as a GeoJSON file: "data/paris_districts_utm.geojson")

* Read the dataset into a GeoDataFrame called `districts`.
* Check the first rows of the dataframe. What kind of geometries does this dataset contain?
* How many features are there in the dataset? (hint: use the `.shape` attribute)
* Make a quick plot of the `districts` dataset (set the figure size to (12, 6)).
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts = geopandas.read_file("data/paris_districts_utm.geojson")
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts.head()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts.shape
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts.plot(figsize=(12, 6))
```

<div class="alert alert-success">

**EXERCISE**:
    
What are the largest districts (biggest area)?

* Calculate the area of each district.
* Add this area as a new column to the `districts` dataframe.
* Sort the dataframe by this area column for largest to smallest values (descending).

<details><summary>Hints</summary>

* Adding a column can be done by assigning values to a column using the same square brackets syntax: `df['new_col'] = values`
* To sort the rows of a DataFrame, use the `sort_values()` method, specifying the colum to sort on with the `by='col_name'` keyword. Check the help of this method to see how to sort ascending or descending.

</details>

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts.geometry.area
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# dividing by 10^6 for showing km²
districts['area'] = districts.geometry.area / 1e6
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts.sort_values(by='area', ascending=False)
```

<div class="alert alert-success">

**EXERCISE**:

* Add a column `'population_density'` representing the number of inhabitants per squared kilometer (Note: The area is given in squared meter, so you will need to multiply the result with `10**6`).
* Plot the districts using the `'population_density'` to color the polygons. For this, use the `column=` keyword.
* Use the `legend=True` keyword to show a color bar.

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Add a population density column
districts['population_density'] = districts['population'] / districts.geometry.area * 10**6
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Make a plot of the districts colored by the population density
districts.plot(column='population_density', figsize=(12, 6), legend=True)
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# As comparison, the misleading plot when not turning the population number into a density
districts.plot(column='population', figsize=(12, 6), legend=True)
```

---

## For the curious: A bit more on importing and creating GeoDataFrames

+++

### Constructing a GeoDataFrame manually

```{code-cell} ipython3
geopandas.GeoDataFrame({
    'geometry': [Point(1, 1), Point(2, 2)],
    'attribute1': [1, 2],
    'attribute2': [0.1, 0.2]})
```

### Creating a GeoDataFrame from an existing dataframe

For example, if you have lat/lon coordinates in two columns:

```{code-cell} ipython3
df = pd.DataFrame(
    {'City': ['Buenos Aires', 'Brasilia', 'Santiago', 'Bogota', 'Caracas'],
     'Country': ['Argentina', 'Brazil', 'Chile', 'Colombia', 'Venezuela'],
     'Latitude': [-34.58, -15.78, -33.45, 4.60, 10.48],
     'Longitude': [-58.66, -47.91, -70.66, -74.08, -66.86]})
```

```{code-cell} ipython3
gdf = geopandas.GeoDataFrame(
    df, geometry=geopandas.points_from_xy(df.Longitude, df.Latitude))
```

```{code-cell} ipython3
gdf
```

See https://geopandas.org/en/latest/gallery/create_geopandas_from_pandas.html for full example
