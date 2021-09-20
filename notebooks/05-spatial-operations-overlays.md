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

<p><font size="6"><b>Spatial operations and overlays: creating new geometries</b></font></p>


> *DS Python for GIS and Geoscience*  
> *October, 2020*
>
> *© 2020, Joris Van den Bossche and Stijn Van Hoey  (<mailto:jorisvandenbossche@gmail.com>, <mailto:stijnvanhoey@gmail.com>). Licensed under [CC BY 4.0 Creative Commons](http://creativecommons.org/licenses/by/4.0/)*

---

+++

In the previous notebook we have seen how to identify and use the spatial relationships between geometries. In this notebook, we will see how to create new geometries based on those relationships.

```{code-cell} ipython3
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
```

```{code-cell} ipython3
countries = geopandas.read_file("zip://./data/ne_110m_admin_0_countries.zip")
cities = geopandas.read_file("zip://./data/ne_110m_populated_places.zip")
rivers = geopandas.read_file("zip://./data/ne_50m_rivers_lake_centerlines.zip")
```

```{code-cell} ipython3
# defining the same example geometries as in the previous notebook
belgium = countries.loc[countries['name'] == 'Belgium', 'geometry'].item()
brussels = cities.loc[cities['name'] == 'Brussels', 'geometry'].item()
```

## Spatial operations

Next to the spatial predicates that return boolean values, Shapely and GeoPandas also provide operations that return new geometric objects.

**Binary operations:**

<table><tr>
<td> <img src="../img/spatial-operations-base.png"/> </td>
<td> <img src="../img/spatial-operations-intersection.png"/> </td>
</tr>
<tr>
<td> <img src="../img/spatial-operations-union.png"/> </td>
<td> <img src="../img/spatial-operations-difference.png"/> </td>
</tr></table>

**Buffer:**

<table><tr>
<td> <img src="../img/spatial-operations-buffer-point1.png"/> </td>
<td> <img src="../img/spatial-operations-buffer-point2.png"/> </td>
</tr>
<tr>
<td> <img src="../img/spatial-operations-buffer-line.png"/> </td>
<td> <img src="../img/spatial-operations-buffer-polygon.png"/> </td>
</tr></table>


See https://shapely.readthedocs.io/en/stable/manual.html#spatial-analysis-methods for more details.

+++

For example, using the toy data from above, let's construct a buffer around Brussels (which returns a Polygon):

```{code-cell} ipython3
geopandas.GeoSeries([belgium, brussels.buffer(1)]).plot(alpha=0.5, cmap='tab10')
```

and now take the intersection, union or difference of those two polygons:

```{code-cell} ipython3
brussels.buffer(1).intersection(belgium)
```

```{code-cell} ipython3
brussels.buffer(1).union(belgium)
```

```{code-cell} ipython3
brussels.buffer(1).difference(belgium)
```

### Spatial operations with GeoPandas

+++

Above we showed how to create a new geometry based on two individual shapely geometries. The same operations can be extended to GeoPandas. Given a GeoDataFrame, we can calculate the intersection, union or difference of each of the geometries with another geometry.

Let's look at an example with a subset of the countries. We have a GeoDataFrame with the country polygons of Africa, and  now consider a rectangular polygon, representing an area around the equator:

```{code-cell} ipython3
africa = countries[countries.continent == 'Africa']
```

```{code-cell} ipython3
from shapely.geometry import LineString
box = LineString([(-10, 0), (50, 0)]).buffer(10, cap_style=3)
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(6, 6))
africa.plot(ax=ax, facecolor='none', edgecolor='k')
geopandas.GeoSeries([box]).plot(ax=ax, facecolor='C0', edgecolor='k', alpha=0.5)
```

The intersection method of the GeoDataFrame will now calculate the intersection with the rectangle for each of the geometries of the africa GeoDataFrame element-wise. Note that for many of the countries, those that do not overlap with the rectangle, this will be an empty geometry:

```{code-cell} ipython3
africa_intersection = africa.intersection(box)
africa_intersection.head()
```

What is returned is a new GeoSeries of the same length as the original dataframe, containing one row per country, but now containing only the intersection. In this example, the last element shown is an empty polygon, as that country was not overlapping with the box.

```{code-cell} ipython3
# remove the empty polygons before plotting
africa_intersection = africa_intersection[~africa_intersection.is_empty]
# plot the intersection
africa_intersection.plot()
```

# Unary union and dissolve

Another useful method is the `unary_union` attribute, which converts the set of geometry objects in a GeoDataFrame into a single geometry object by taking the union of all those geometries.

For example, we can construct a single Shapely geometry object for the Africa continent:

```{code-cell} ipython3
africa_countries = countries[countries['continent'] == 'Africa']
```

```{code-cell} ipython3
africa = africa_countries.unary_union
```

```{code-cell} ipython3
africa
```

```{code-cell} ipython3
print(str(africa)[:1000])
```

Alternatively, you might want to take the unary union of a set of geometries but *grouped* by one of the attributes of the GeoDataFrame (so basically doing "groupby" + "unary_union"). For this operation, GeoPandas provides the `dissolve()` method:

```{code-cell} ipython3
continents = countries.dissolve(by="continent")   # , aggfunc="sum"
```

```{code-cell} ipython3
continents
```

<div class="alert alert-info" style="font-size:120%">

**REMEMBER**:

GeoPandas (and Shapely for the individual objects) provide a whole lot of basic methods to analyze the geospatial data (distance, length, centroid, boundary, convex_hull, simplify, transform, ....), much more than what we can touch in this tutorial.

An overview of all methods provided by GeoPandas can be found here: https://geopandas.readthedocs.io/en/latest/docs/reference.html


</div>

+++

## Let's practice!

+++

<div class="alert alert-success">

**EXERCISE: What are the districts close to the Seine?**

Below, the coordinates for the Seine river in the neighborhood of Paris are provided as a GeoJSON-like feature dictionary (created at http://geojson.io). 

Based on this `seine` object, we want to know which districts are located close (maximum 150 m) to the Seine. 

* Create a buffer of 150 m around the Seine.
* Check which districts intersect with this buffered object.
* Make a visualization of the districts indicating which districts are located close to the Seine.
 
</div>

```{code-cell} ipython3
:clear_cell: false

districts = geopandas.read_file("data/paris_districts.geojson").to_crs(epsg=2154)
```

```{code-cell} ipython3
:clear_cell: false

# created a line with http://geojson.io
s_seine = geopandas.GeoDataFrame.from_features({"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"LineString","coordinates":[[2.408924102783203,48.805619828930226],[2.4092674255371094,48.81703747481909],[2.3927879333496094,48.82325391133874],[2.360687255859375,48.84912860497674],[2.338714599609375,48.85827758964043],[2.318115234375,48.8641501307046],[2.298717498779297,48.863246707697],[2.2913360595703125,48.859519915404825],[2.2594070434570312,48.8311646245967],[2.2436141967773438,48.82325391133874],[2.236919403076172,48.82347994904826],[2.227306365966797,48.828339513221444],[2.2224998474121094,48.83862215329593],[2.2254180908203125,48.84856379804802],[2.2240447998046875,48.85409863123821],[2.230224609375,48.867989496547864],[2.260265350341797,48.89192242750887],[2.300262451171875,48.910203080780285]]}}]},
                                               crs='EPSG:4326')
```

```{code-cell} ipython3
# convert to local UTM zone
s_seine_utm = s_seine.to_crs(epsg=2154)
```

```{code-cell} ipython3
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(20, 10))
districts.plot(ax=ax, color='grey', alpha=0.4, edgecolor='k')
s_seine_utm.plot(ax=ax)
```

```{code-cell} ipython3
# access the single geometry object
seine = s_seine_utm.geometry.item()
seine
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Take a buffer
seine_buffer = seine.buffer(150)
seine_buffer
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Use the intersection
districts_seine = districts[districts.intersects(seine_buffer)]
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Make a plot
fig, ax = plt.subplots(figsize=(20, 10))
districts.plot(ax=ax, color='grey', alpha=0.4, edgecolor='k')
districts_seine.plot(ax=ax, color='blue', alpha=0.4, edgecolor='k')
s_seine_utm.plot(ax=ax)
```

------

+++

<div class="alert alert-success">

**EXERCISE: Exploring a Land Use dataset**

For the following exercises, we first introduce a new dataset: a dataset about the land use of Paris (a simplified version based on the open European [Urban Atlas](https://land.copernicus.eu/local/urban-atlas)). The land use indicates for what kind of activity a certain area is used, such as residential area or for recreation. It is a polygon dataset, with a label representing the land use class for different areas in Paris.

In this exercise, we will read the data, explore it visually, and calculate the total area of the different classes of land use in the area of Paris.

* Read in the `'paris_land_use.shp'` file and assign the result to a variable `land_use`.
* Make a plot of `land_use`, using the `'class'` column to color the polygons. Add a legend with `legend=True`, and make the figure size a bit larger.
* Add a new column `'area'` to the dataframe with the area of each polygon.
* Calculate the total area in km² for each `'class'` using the `groupby()` method, and print the result.

<details><summary>Hints</summary>

* Reading a file can be done with the `geopandas.read_file()` function.
* To use a column to color the geometries, use the `column` keyword to indicate the column name.
* The area of each geometry can be accessed with the `area` attribute of the `geometry` of the GeoDataFrame.
* The `groupby()` method takes the column name on which you want to group as the first argument.

</details>

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Import the land use dataset
land_use = geopandas.read_file("data/paris_land_use.zip")
land_use.head()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Make a plot of the land use with 'class' as the color
land_use.plot(column='class', legend=True, figsize=(15, 10))
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Add the area as a new column
land_use['area'] = land_use.geometry.area
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Calculate the total area for each land use class
total_area = land_use.groupby('class')['area'].sum() / 1000**2
total_area
```

<div class="alert alert-success">

**EXERCISE: Intersection of two polygons**

For this exercise, we are going to use 2 individual polygons: the district of Muette extracted from the `districts` dataset, and the green urban area of Boulogne, a large public park in the west of Paris, extracted from the `land_use` dataset. The two polygons have already been assigned to the `muette` and `park_boulogne` variables.

We first visualize the two polygons. You will see that they overlap, but the park is not fully located in the district of Muette. Let's determine the overlapping part:

* Plot the two polygons in a single map to examine visually the degree of overlap
* Calculate the intersection of the `park_boulogne` and `muette` polygons.
* Plot the intersection.
* Print the proportion of the area of the district that is occupied by the park.

<details><summary>Hints</summary>

* To plot single Shapely objects, you can put those in a `GeoSeries([..])` to use the GeoPandas `plot()` method.
* The intersection of to scalar polygons can be calculated with the `intersection()` method of one of the polygons, and passing the other polygon as the argument to that method.

</details>

</div>

```{code-cell} ipython3
land_use = geopandas.read_file("data/paris_land_use.zip")
districts = geopandas.read_file("data/paris_districts.geojson").to_crs(land_use.crs)
```

```{code-cell} ipython3
# extract polygons
land_use['area'] = land_use.geometry.area
park_boulogne = land_use[land_use['class'] == "Green urban areas"].sort_values('area').geometry.iloc[-1]
muette = districts[districts.district_name == 'Muette'].geometry.item()
```

```{code-cell} ipython3
# Plot the two polygons
geopandas.GeoSeries([park_boulogne, muette]).plot(alpha=0.5, color=['green', 'blue'])
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Calculate the intersection of both polygons
intersection = park_boulogne.intersection(muette)
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Plot the intersection
geopandas.GeoSeries([intersection]).plot()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Print proportion of district area that occupied park
print(intersection.area / muette.area)
```

<div class="alert alert-success">

**EXERCISE: Intersecting a GeoDataFrame with a Polygon**

Combining the land use dataset and the districts dataset, we can now investigate what the land use is in a certain district.

For that, we first need to determine the intersection of the land use dataset with a given district. Let's take again the *Muette* district as example case.

* Calculate the intersection of the `land_use` polygons with the single `muette` polygon. Call the result `land_use_muette`.
* Remove the empty geometries from `land_use_muette`.
* Make a quick plot of this intersection, and pass `edgecolor='black'` to more clearly see the boundaries of the different polygons.
* Print the first five rows of `land_use_muette`.

<details><summary>Hints</summary>

* The intersection of each geometry of a GeoSeries with another single geometry can be performed with the `intersection()` method of a GeoSeries.
* The `intersection()` method takes as argument the geometry for which to calculate the intersection.
* We can check which geometries are empty with the `is_empty` attribute of a GeoSeries.
    
</details>

</div>

```{code-cell} ipython3
land_use = geopandas.read_file("data/paris_land_use.zip")
districts = geopandas.read_file("data/paris_districts.geojson").to_crs(land_use.crs)
muette = districts[districts.district_name == 'Muette'].geometry.item()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Calculate the intersection of the land use polygons with Muette
land_use_muette = land_use.geometry.intersection(muette)
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Print the first five rows of the intersection
land_use_muette.head()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Remove the empty geometries
land_use_muette = land_use_muette[~land_use_muette.is_empty]
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Print the first five rows of the intersection
land_use_muette.head()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Plot the intersection
land_use_muette.plot(edgecolor='black')
```

You can see in the plot that we now only have a subset of the full land use dataset. The original `land_use_muette` (before removing the empty geometries) still has the same number of rows as the original `land_use`, though. But many of the rows, as you could see by printing the first rows, consist now of empty polygons when it did not intersect with the Muette district.

The `intersection()` method also returned only geometries. If we want to combine those intersections with the attributes of the original land use, we can take a copy of this and replace the geometries with the intersections (you can uncomment and run to see the code):

```{code-cell} ipython3
:tags: [nbtutor-solution]

land_use_muette = land_use.copy()
land_use_muette['geometry'] = land_use.geometry.intersection(muette)
land_use_muette = land_use_muette[~land_use_muette.is_empty]
land_use_muette.head()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

land_use_muette.plot(column="class") #edgecolor="black")
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

land_use_muette.dissolve(by='class')
```

<div class="alert alert-success">

**EXERCISE: The land use of the Muette district**

Based on the `land_use_muette` dataframe with the land use for the Muette districts as calculated above, we can now determine the total area of the different land use classes in the Muette district.

* Calculate the total area per land use class.
* Calculate the fraction (in percentage) for the different land use classes.

<details><summary>Hints</summary>

* The intersection of each geometry of a GeoSeries with another single geometry can be performed with the `intersection()` method of a GeoSeries.
* The `intersection()` method takes as argument the geometry for which to calculate the intersection.
* We can check which geometries are empty with the `is_empty` attribute of a GeoSeries.
    
</details>

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

land_use_muette['area'] = land_use_muette.geometry.area
# Total land use per class
land_use_muette.groupby("class")["area"].sum()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Relative percentage of land use classes
land_use_muette.groupby("class")["area"].sum() / land_use_muette.geometry.area.sum() * 100
```

The above was only for a single district. If we want to do this more easily for all districts, we can do this with the overlay operation.

+++

## The overlay operation

In a spatial join operation, we are not changing the geometries itself. We are not joining geometries, but joining attributes based on a spatial relationship between the geometries. This also means that the geometries need to at least overlap partially.

If you want to create new geometries based on joining (combining) geometries of different dataframes into one new dataframe (eg by taking the intersection of the geometries), you want an **overlay** operation.

+++

### How does it differ compared to the intersection method?

+++

With the `intersection()` method introduced in the previous section, we could for example determine the intersection of a set of countries with another polygon, a circle in the example below:

<img width="70%" src="../img/geopandas/chapter3-overlay-countries-circle-intersection-new.png"/>

+++

However, this method (`countries.intersection(circle)`) also has some limitations.

* Mostly useful when intersecting a GeoSeries with a single polygon.
* Does not preserve attribute information of the intersecting polygons.

For cases where we require a bit more complexity, it is preferable to use the "overlay" operation, instead of the intersection method.

+++

Consider the following simplified example. On the left we see again the 3 countries. On the right we have the plot of a GeoDataFrame with some simplified geologic regions for the same area:

<table width="80%"><tr>
<td> <img src="../img/geopandas/chapter3-overlay-countries.png"/> </td>
<td> <img src="../img/geopandas/chapter3-overlay-regions.png"/> </td>
</tr></table>

By simply plotting them on top of each other, as shown below, you can see that the polygons of both layers intersect. 

But now, by "overlaying" the two layers, we can create a third layer that contains the result of intersecting both layers: all the intersections of each country with each geologic region. It keeps only those areas that were included in both layers.

<table width="80%"><tr>
<td> <img src="../img/geopandas/chapter3-overlay-both.png"/> </td>
<td> <img src="../img/geopandas/chapter3-overlay-overlayed.png"/> </td>
</tr></table>

This operation is called an intersection overlay, and in GeoPandas we can perform this operation with the `geopandas.overlay()` function.

+++

Another code example:

```{code-cell} ipython3
africa = countries[countries['continent'] == 'Africa']
```

```{code-cell} ipython3
africa.plot()
```

```{code-cell} ipython3
cities['geometry'] = cities.buffer(2)
```

```{code-cell} ipython3
intersection = geopandas.overlay(africa, cities, how='intersection')
intersection.plot()
```

```{code-cell} ipython3
intersection.head()
```

With the overlay method, we pass the full GeoDataFrame with all regions to intersect the countries with. The result contains all non-empty intersections of all combinations of countries and city regions.

Note that the result of the overlay function also keeps the attribute information of both the countries as the city regions. That can be very useful for further analysis.

```{code-cell} ipython3
geopandas.overlay(africa, cities, how='intersection').plot()  # how="difference"/"union"/"symmetric_difference"
```

<div class="alert alert-info" style="font-size:120%">
<b>REMEMBER</b> <br>

* **Spatial join**: transfer attributes from one dataframe to another based on the spatial relationship
* **Spatial overlay**: construct new geometries based on spatial operation between both dataframes (and combining attributes of both dataframes)

</div>

+++

## Let's practice!

+++

<div class="alert alert-success">

**EXERCISE: Overlaying spatial datasets I**

We will now combine both datasets in an overlay operation. Create a new `GeoDataFrame` consisting of the intersection of the land use polygons which each of the districts, but make sure to bring the attribute data from both source layers.

* Create a new GeoDataFrame from the intersections of `land_use` and `districts`. Assign the result to a variable `combined`.
* Print the first rows the resulting GeoDataFrame (`combined`).

<details><summary>Hints</summary>

* The intersection of two GeoDataFrames can be calculated with the `geopandas.overlay()` function.
* The `overlay()` functions takes first the two GeoDataFrames to combine, and a third `how` keyword indicating how to combine the two layers.
* For making an overlay based on the intersection, you can pass `how='intersection'`.

</details>

</div>

```{code-cell} ipython3
land_use = geopandas.read_file("data/paris_land_use.zip")
districts = geopandas.read_file("data/paris_districts.geojson").to_crs(land_use.crs)
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Overlay both datasets based on the intersection
combined = geopandas.overlay(land_use, districts, how='intersection')
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Print the first five rows of the result
combined.head()
```

<div class="alert alert-success">

**EXERCISE: Overlaying spatial datasets II**

Now that we created the overlay of the land use and districts datasets, we can more easily inspect the land use for the different districts. Let's get back to the example district of Muette, and inspect the land use of that district.

* Add a new column `'area'` with the area of each polygon to the `combined` GeoDataFrame.
* Create a subset called `land_use_muette` where the `'district_name'` is equal to "Muette".
* Make a plot of `land_use_muette`, using the `'class'` column to color the polygons.
* Calculate the total area for each `'class'` of `land_use_muette` using the `groupby()` method, and print the result.

<details><summary>Hints</summary>

* The area of each geometry can be accessed with the `area` attribute of the `geometry` of the GeoDataFrame.
* To use a column to color the geometries, pass its name to the `column` keyword.
* The `groupby()` method takes the column name on which you want to group as the first argument.
* The total area for each class can be calculated by taking the `sum()` of the area.

</details>

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Add the area as a column
combined['area'] = combined.geometry.area
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Take a subset for the Muette district
land_use_muette = combined[combined['district_name'] == 'Muette']
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Visualize the land use of the Muette district
land_use_muette.plot(column='class')
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

# Calculate the total area for each land use class
print(land_use_muette.groupby('class')['area'].sum() / 1000**2)
```

<div class="alert alert-success">

**EXERCISE: Overlaying spatial datasets III**

Thanks to the result of the overlay operation, we can now more easily perform a similar analysis for *all* districts. Let's investigate the fraction of green urban area in each of the districts.

* Based on the `combined` dataset, calculate the total area per district using `groupby()`.
* Select the subset of "Green urban areas" from `combined` and call this `urban_green`.
* Now calculate the total area per district for this `urban_green` subset, and call this `urban_green_area`.
* Determine the fraction of urban green area in each district.

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts_area = combined.groupby("district_name")["area"].sum()
districts_area.head()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

urban_green = combined[combined["class"] == "Green urban areas"]
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

urban_green_area = urban_green.groupby("district_name")["area"].sum()
urban_green_area.head()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

urban_green_fraction = urban_green_area / districts_area * 100
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

urban_green_fraction.nlargest()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

urban_green_fraction.nsmallest()
```

An alternative to calculate the area per land use class in each district:

```{code-cell} ipython3
combined.groupby(["district_name", "class"])["area"].sum().reset_index()
```

```{code-cell} ipython3

```
