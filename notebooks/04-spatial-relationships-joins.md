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

<p><font size="6"><b>Spatial relationships and joins</b></font></p>


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

```{code-cell} ipython3
countries = geopandas.read_file("data/ne_110m_admin_0_countries.zip")
cities = geopandas.read_file("data/ne_110m_populated_places.zip")
rivers = geopandas.read_file("data/ne_50m_rivers_lake_centerlines.zip")
```

## Spatial relationships

An important aspect of geospatial data is that we can look at *spatial relationships*: how two spatial objects relate to each other (whether they overlap, intersect, contain, .. one another).

The topological, set-theoretic relationships in GIS are typically based on the DE-9IM model. See https://en.wikipedia.org/wiki/Spatial_relation for more information.

![](../img/TopologicSpatialRelarions2.png)
(Image by [Krauss, CC BY-SA 3.0](https://en.wikipedia.org/wiki/Spatial_relation#/media/File:TopologicSpatialRelarions2.png))

+++

### Relationships between individual objects

+++

Let's first create some small toy spatial objects:

A polygon <small>(note: we use `.item()` here to to extract the scalar geometry object from the GeoSeries of length 1)</small>:

```{code-cell} ipython3
belgium = countries.loc[countries['name'] == 'Belgium', 'geometry'].item()
```

Two points:

```{code-cell} ipython3
paris = cities.loc[cities['name'] == 'Paris', 'geometry'].item()
brussels = cities.loc[cities['name'] == 'Brussels', 'geometry'].item()
```

And a linestring:

```{code-cell} ipython3
from shapely.geometry import LineString
line = LineString([paris, brussels])
```

Let's visualize those 4 geometry objects together (I only put them in a GeoSeries to easily display them together with the geopandas `.plot()` method):

```{code-cell} ipython3
geopandas.GeoSeries([belgium, paris, brussels, line]).plot(cmap='tab10')
```

You can recognize the abstract shape of Belgium.

Brussels, the capital of Belgium, is thus located within Belgium. This is a spatial relationship, and we can test this using the individual shapely geometry objects as follow:

```{code-cell} ipython3
brussels.within(belgium)
```

And using the reverse, Belgium contains Brussels:

```{code-cell} ipython3
belgium.contains(brussels)
```

On the other hand, Paris is not located in Belgium:

```{code-cell} ipython3
belgium.contains(paris)
```

```{code-cell} ipython3
paris.within(belgium)
```

The straight line we draw from Paris to Brussels is not fully located within Belgium, but it does intersect with it:

```{code-cell} ipython3
belgium.contains(line)
```

```{code-cell} ipython3
line.intersects(belgium)
```

### Spatial relationships with GeoDataFrames

The same methods that are available on individual `shapely` geometries as we have seen above, are also available as methods on `GeoSeries` / `GeoDataFrame` objects.

For example, if we call the `contains` method on the world dataset with the `paris` point, it will do this spatial check for each country in the `world` dataframe:

```{code-cell} ipython3
countries.contains(paris)
```

Because the above gives us a boolean result, we can use that to filter the dataframe:

```{code-cell} ipython3
countries[countries.contains(paris)]
```

And indeed, France is the only country in the world in which Paris is located.

+++

Another example, extracting the linestring of the Amazon river in South America, we can query through which countries the river flows:

```{code-cell} ipython3
amazon = rivers[rivers['name'] == 'Amazonas'].geometry.item()
```

```{code-cell} ipython3
countries[countries.crosses(amazon)]  # or .intersects
```

<div class="alert alert-info" style="font-size:120%">

**REFERENCE**:

Overview of the different functions to check spatial relationships (*spatial predicate functions*):

* `equals`
* `contains`
* `crosses`
* `disjoint`
* `intersects`
* `overlaps`
* `touches`
* `within`
* `covers`
* `covered_by`


See https://shapely.readthedocs.io/en/stable/manual.html#predicates-and-relationships for an overview of those methods.

See https://en.wikipedia.org/wiki/DE-9IM for all details on the semantics of those operations.

</div>

+++

## Let's practice!

We will again use the Paris datasets to exercise. Let's start importing them again, and directly converting both to the local projected CRS:

```{code-cell} ipython3
districts = geopandas.read_file("data/paris_districts.geojson").to_crs(epsg=2154)
stations = geopandas.read_file("data/paris_bike_stations.geojson").to_crs(epsg=2154)
```

<div class="alert alert-success">

**EXERCISE: The Eiffel Tower**

The Eiffel Tower is an iron lattice tower built in the 19th century, and is probably the most iconic view of Paris.

The location of the Eiffel Tower is: x of 648237.3 and y of 6862271.9

* Create a Shapely point object with the coordinates of the Eiffel Tower and assign it to a variable called `eiffel_tower`. Print the result.
* Check if the Eiffel Tower is located within the Montparnasse district (provided).
* Check if the Montparnasse district contains the bike station location.
* Calculate the distance between the Eiffel Tower and the bike station (note: in this case, the distance is returned in meters).


<details><summary>Hints</summary>

* The `Point` class is available in the `shapely.geometry` submodule
* Creating a point can be done by passing the x and y coordinates to the `Point()` constructor.
* The `within()` method checks if the object is located within the passed geometry (used as `geometry1.within(geometry2)`).
* The `contains()` method checks if the object contains the passed geometry (used as `geometry1.contains(geometry2)`).
* To calculate the distance between two geometries, the `distance()` method of one of the geometries can be used.

</details>

</div>

```{code-cell} ipython3
# Import the Point geometry
from shapely.geometry import Point
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Construct a point object for the Eiffel Tower
eiffel_tower = Point(648237.3, 6862271.9)
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Print the result
print(eiffel_tower)
```

```{code-cell} ipython3
# Accessing the Montparnasse geometry (Polygon)
district_montparnasse = districts.loc[districts['district_name'] == 'Montparnasse', 'geometry'].item()
bike_station = stations.loc[stations['name'] == '14033 - DAGUERRE GASSENDI', 'geometry'].item()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Is the Eiffel Tower located within the Montparnasse district?
print(eiffel_tower.within(district_montparnasse))
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Does the Montparnasse district contains the bike station?
print(district_montparnasse.contains(bike_station))
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# The distance between the Eiffel Tower and the bike station?
print(eiffel_tower.distance(bike_station))
```

<div class="alert alert-success">

**EXERCISE: In which district in the Eiffel Tower located?**

In previous exercise, we constructed a `Point` geometry for its location, and we checked that it was not located in the Montparnasse district. Let's now determine in which of the districts of Paris it *is* located.

* Create a boolean mask (or filter) indicating whether each district contains the Eiffel Tower or not. Call the result `mask`.
* Filter the `districts` dataframe with the boolean mask and print the result.


<details><summary>Hints</summary>

* To check for each polygon in the districts dataset if it contains a single point, we can use the `contains()` method of the `districts` GeoDataFrame.
* Filtering the rows of a DataFrame based on a condition can be done by passing the boolean mask into `df[..]`.

</details>

</div>

```{code-cell} ipython3
# Construct a point object for the Eiffel Tower
eiffel_tower = Point(648237.3, 6862271.9)
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Create a boolean Series
mask = districts.contains(eiffel_tower)
mask
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Filter the districts with the boolean mask
districts[mask]
```

<div class="alert alert-success">

**EXERCISE: How far is the closest bike station?**

Now, we might be interested in the bike stations nearby the Eiffel Tower. To explore them, let's visualize the Eiffel Tower itself as well as the bikes stations within 1km.

To do this, we can calculate the distance to the Eiffel Tower for each of the stations. Based on this result, we can then create a mask that takes `True` if the station is within 1km, and `False` otherwise, and use it to filter the stations GeoDataFrame. Finally, we make a visualization of this subset.

* Calculate the distance to the Eiffel Tower for each station, and call the result `dist_eiffel`.
* Print the distance to the closest station (which is the minimum of `dist_eiffel`).
* Select the rows the `stations` GeoDataFrame where the distance to the Eiffel Tower is less than 1 km (note that the distance is in meters). Call the result `stations_eiffel`.

<details><summary>Hints</summary>

* The `.distance()` method of a GeoDataFrame works element-wise: it calculates the distance between each geometry in the GeoDataFrame and the geometry passed to the method.
* A Series has a `.min()` method to calculate the minimum value.
* To create a boolean mask based on a condition, we can do e.g. `s < 100`.

</details>

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

# The distance from each stations to the Eiffel Tower
dist_eiffel = stations.distance(eiffel_tower)
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# The distance to the closest station
dist_eiffel.min()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Filter the bike stations closer than 1 km
stations_eiffel = stations[dist_eiffel < 1000]
```

```{code-cell} ipython3
# Make a plot of the close-by bike stations using matplotlib and contextily
import matplotlib.pyplot as plt
import contextily

fig, ax = plt.subplots(figsize=(8, 8))
stations_eiffel.plot(ax=ax)
geopandas.GeoSeries([eiffel_tower], crs='EPSG:2154').plot(ax=ax, color='red')
contextily.add_basemap(ax, crs=stations_eiffel.crs)
ax.set_axis_off()
```

```{code-cell} ipython3
# Make a plot of the close-by bike stations using matplotlib and contextily
m = stations_eiffel.explore(marker_kwds=dict(radius=5))
geopandas.GeoSeries([eiffel_tower], crs='EPSG:2154').explore(m=m, color='red', marker_kwds=dict(radius=5))
```

---

+++

## Spatial joins

+++

In the previous section of this notebook, we could use the spatial relationship methods to check in which country a certain city was located. But what if we wanted to perform this same operation for every city and country? For example, we might want to know for each city in which country it is located.  

In tabular jargon, this would imply adding a column to our cities dataframe with the name of the country in which it is located. Since country name is contained in the countries dataset, we need to combine - or "join" - information from both datasets. Joining on location (rather than on a shared column) is called a "spatial join".

So here we will do:

- Based on the `countries` and `cities` dataframes, determine for each city the country in which it is located.
- To solve this problem, we will use the the concept of a "spatial join" operation: combining information of geospatial datasets based on their spatial relationship.

+++

### Recap - joining dataframes

Pandas provides functionality to join or merge dataframes in different ways, see https://chrisalbon.com/python/data_wrangling/pandas_join_merge_dataframe/ for an overview and https://pandas.pydata.org/pandas-docs/stable/merging.html for the full documentation.

+++

To illustrate the concept of joining the information of two dataframes with pandas, let's take a small subset of our `cities` and `countries` datasets:

```{code-cell} ipython3
cities2 = cities[cities['name'].isin(['Bern', 'Brussels', 'London', 'Paris'])].copy()
cities2['iso_a3'] = ['CHE', 'BEL', 'GBR', 'FRA']
```

```{code-cell} ipython3
cities2
```

```{code-cell} ipython3
countries2 = countries[['iso_a3', 'name', 'continent']]
countries2.head()
```

We added a 'iso_a3' column to the `cities` dataset, indicating a code of the country of the city. This country code is also present in the `countries` dataset, which allows us to merge those two dataframes based on the common column.

Joining the `cities` dataframe with `countries` will transfer extra information about the countries (the full name, the continent) to the `cities` dataframe, based on a common key:

```{code-cell} ipython3
cities2.merge(countries2, on='iso_a3')
```

**But** for this illustrative example we added the common column manually, it is not present in the original dataset. However, we can still know how to join those two datasets based on their spatial coordinates.

+++

### Recap - spatial relationships between objects

In the previous section, we have seen the notion of spatial relationships between geometry objects: within, contains, intersects, ...

In this case, we know that each of the cities is located *within* one of the countries, or the other way around that each country can *contain* multiple cities.

We can test such relationships using the methods we have seen in the previous notebook:

```{code-cell} ipython3
france = countries.loc[countries['name'] == 'France', 'geometry'].item()
```

```{code-cell} ipython3
cities.within(france)
```

The above gives us a boolean series, indicating for each point in our `cities` dataframe whether it is located within the area of France or not.  
Because this is a boolean series as result, we can use it to filter the original dataframe to only show those cities that are actually within France:

```{code-cell} ipython3
cities[cities.within(france)]
```

We could now repeat the above analysis for each of the countries, and add a column to the `cities` dataframe indicating this country. However, that would be tedious to do manually, and is also exactly what the spatial join operation provides us.

*(note: the above result is incorrect, but this is just because of the coarse-ness of the countries dataset)*

+++

## Spatial join operation

<div class="alert alert-info" style="font-size:120%">

**SPATIAL JOIN** = *transferring attributes from one layer to another based on their spatial relationship* <br>


Different parts of this operations:

* The GeoDataFrame to which we want add information
* The GeoDataFrame that contains the information we want to add
* The spatial relationship ("predicate") we want to use to match both datasets ('intersects', 'contains', 'within')
* The type of join: left or inner join


![](../img/illustration-spatial-join.svg)

</div>

+++

In this case, we want to join the `cities` dataframe with the information of the `countries` dataframe, based on the spatial relationship between both datasets.

We use the [`geopandas.sjoin`](http://geopandas.readthedocs.io/en/latest/reference/geopandas.sjoin.html) function:

```{code-cell} ipython3
joined = geopandas.sjoin(cities, countries, predicate='within', how='left')
```

```{code-cell} ipython3
joined
```

```{code-cell} ipython3
joined[joined["name_right"] == "France"]
```

```{code-cell} ipython3
joined['continent'].value_counts()
```

## Let's practice!

We will again use the Paris datasets to do some exercises. Let's start importing them:

```{code-cell} ipython3
districts = geopandas.read_file("data/paris_districts.geojson").to_crs(epsg=2154)
stations = geopandas.read_file("data/paris_bike_stations.geojson").to_crs(epsg=2154)
```

<div class="alert alert-success">

**EXERCISE:**

* Determine for each bike station in which district it is located (using a spatial join!). Call the result `joined`.

<details><summary>Hints</summary>

- The `geopandas.sjoin()` function takes as first argument the dataframe to which we want to add information, and as second argument the dataframe that contains this additional information.

</details>

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

joined = geopandas.sjoin(stations, districts[['district_name', 'geometry']], predicate='within')
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

joined.head()
```

<div class="alert alert-success">

**EXERCISE: Map of tree density by district (I)**

Using a dataset of all trees in public spaces in Paris, the goal is to make a map of the tree density by district. We first need to find out how many trees each district contains, which we will do in this exercise. In the following exercise, we will use this result to calculate the density and create a map.

To obtain the tree count by district, we first need to know in which district each tree is located, which we can do with a spatial join. Then, using the result of the spatial join, we will calculate the number of trees located in each district using the pandas 'group-by' functionality.

- Import the trees dataset `"paris_trees.gpkg"` and call the result `trees`. Also read the districts dataset we have seen previously (`"paris_districts.geojson"`), and call this `districts`. Convert the districts dataset to the same CRS as the trees dataset.
- Add a column with the `'district_name'` to the trees dataset using a spatial join. Call the result `joined`.

<details><summary>Hints</summary>

- Remember, we can perform a spatial join with the `geopandas.sjoin()` function.
- `geopandas.sjoin()` takes as first argument the dataframe to which we want to add information, and as second argument the dataframe that contains this additional information.
- The `op` argument is used to specify which spatial relationship between both dataframes we want to use for joining (options are `'intersects'`, `'contains'`, `'within'`).

</details>

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Read the trees and districts data
trees = geopandas.read_file("data/paris_trees.gpkg")
districts = geopandas.read_file("data/paris_districts.geojson").to_crs(trees.crs)
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# The trees dataset with point locations of trees
trees.head()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Spatial join of the trees and districts datasets
joined = geopandas.sjoin(trees, districts, predicate='within')
joined.head()
```

<div class="alert alert-success">

**EXERCISE: Map of tree density by district (II)**

Calculate the number of trees located in each district: group the `joined` DataFrame by the `'district_name'` column, and calculate the size of each group. Call the resulting Series `trees_by_district`.  <br>

We then convert `trees_by_district` to a DataFrame for the next exercise.

<details><summary>Hints</summary>

- The general group-by syntax in pandas is: `df.groupby('key').aggregation_method()`, substituting 'key' and 'aggregation_method' with the appropriate column name and method. 
- To know the size of groups, we can use the `.size()` method.

</details>

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Calculate the number of trees in each district
trees_by_district = joined.groupby('district_name').size()
```

```{code-cell} ipython3
# Convert the series to a DataFrame and specify column name
trees_by_district = trees_by_district.to_frame(name='n_trees')
```

```{code-cell} ipython3
# Inspect the result
trees_by_district.head()
```

<div class="alert alert-success">

**EXERCISE: Map of tree density by district (III)**

Now we have obtained the number of trees by district, we can make the map of the districts colored by the tree density.

For this, we first need to merge the number of trees in each district we calculated in the previous step (`trees_by_district`) back to the districts dataset. We will use the [`pd.merge()`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.merge.html) function to join two dataframes based on a common column.

Since not all districts have the same size, we should compare the tree density for the visualisation: the number of trees relative to the area.

- Use the `pd.merge()` function to merge `districts` and `trees_by_district` dataframes on the `'district_name'` column. Call the result `districts_trees`.
- Add a column `'n_trees_per_area'` to the `districts_trees` dataframe, based on the `'n_trees'` column divided by the area.
- Make a plot of the `districts_trees` dataframe, using the `'n_trees_per_area'` column to determine the color of the polygons.


<details><summary>Hints</summary>

- The pandas `pd.merge()` function takes the two dataframes you want to merge as the first two arguments.
- The column name on which you want to merge both datasets can be specified with the `on` keyword.
- Accessing a column of a DataFrame can be done with `df['col']`, while adding a column to a DataFrame can be done with `df['new_col'] = values` where `values` can be the result of a computation.
- Remember, the area of each geometry in a GeoSeries or GeoDataFrame can be retrieved using the `area` attribute. So considering a GeoDataFrame `gdf`, then `gdf.geometry.area` will return a Series with the area of each geometry.
- We can use the `.plot()` method of a GeoDataFrame to make a visualization of the geometries. 
- For using one of the columns of the GeoDataFrame to determine the fill color, use the `column=` keyword.


</details>

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Merge the 'districts' and 'trees_by_district' dataframes
districts_trees = pd.merge(districts, trees_by_district, on='district_name')
districts_trees.head()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Add a column with the tree density
districts_trees['n_trees_per_area'] = districts_trees['n_trees'] / districts_trees.geometry.area
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Make of map of the districts colored by 'n_trees_per_area'
ax = districts_trees.plot(column='n_trees_per_area', figsize=(12, 6))
ax.set_axis_off()
```

```{code-cell} ipython3

```
