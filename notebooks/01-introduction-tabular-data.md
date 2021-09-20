---
jupytext:
  formats: ipynb,md:myst
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

<p><font size="6"><b> Introduction to working with pandas and tabular data</b></font></p>


> *DS Python for GIS and Geoscience*  
> *October, 2020*
>
> *© 2020, Joris Van den Bossche and Stijn Van Hoey  (<mailto:jorisvandenbossche@gmail.com>, <mailto:stijnvanhoey@gmail.com>). Licensed under [CC BY 4.0 Creative Commons](http://creativecommons.org/licenses/by/4.0/)*

---

+++

## Working with tabular data using Pandas

+++

To load the pandas package and start working with it, we first import the package. The community agreed alias for pandas is `pd`,  which we will also use here:

```{code-cell} ipython3
import pandas as pd
```

Let's start with importing some actual data. Pandas provides functions for many different formats, but here we will read a simple CSV file with information about the countries of the world:

```{code-cell} ipython3
countries = pd.read_csv("data/countries.csv")
```

```{code-cell} ipython3
countries
```

The object created here is a **DataFrame**:

```{code-cell} ipython3
type(countries)
```

A `DataFrame` is a 2-dimensional, **tablular data structure** comprised of rows and columns. It is similar to a spreadsheet, a database (SQL) table or the data.frame in R.

<img align="center" width=50% src="../img/pandas/01_table_dataframe1.svg">

+++

A DataFrame can store data of different types (including characters, integers, floating point values, categorical data and more) in columns. In pandas, we can check the data types of the columns with the `dtypes` attribute:

```{code-cell} ipython3
countries.dtypes
```

### Each column in a `DataFrame` is a `Series`

When selecting a single column of a pandas `DataFrame`, the result is a pandas `Series`, a 1-dimensional data structure. 

To select the column, use the column label in between square brackets `[]`.

```{code-cell} ipython3
countries['pop_est']
```

```{code-cell} ipython3
s = countries['pop_est']
type(s)
```

### Pandas objects have attributes and methods

Pandas provides a lot of functionalities for the DataFrame and Series. The `.dtypes` shown above is an *attribute* of the DataFrame. In addition, there are also functions that can be called on a DataFrame or Series, i.e. *methods*. As methods are functions, do not forget to use parentheses `()`.

A few examples that can help exploring the data:

```{code-cell} ipython3
countries.head() # Top rows
```

```{code-cell} ipython3
countries.tail() # Bottom rows
```

The ``describe`` method computes summary statistics for each column:

```{code-cell} ipython3
countries['pop_est'].describe()
```

**Sort**ing your data **by** a specific column is another important first-check:

```{code-cell} ipython3
countries.sort_values(by='pop_est')
```

## Basic operations on Series and DataFrames

+++

### Elementwise-operations

+++

The typical arithmetic (+, -, \*, /) and comparison (==, >, <, ...) operations work *element-wise*.

With as scalar:

```{code-cell} ipython3
population = countries['pop_est'].head()
population
```

```{code-cell} ipython3
population / 1000
```

```{code-cell} ipython3
population > 1_000_000
```

With two Series objects:

```{code-cell} ipython3
countries['gdp_md_est'] / countries['pop_est']
```

### Aggregations (reductions)

+++

Pandas provides a large set of **summary** functions that operate on different kinds of pandas objects (DataFrames, Series, Index) and produce a single value. When applied to a DataFrame, the result is returned as a pandas Series (one value for each column).

+++

The average population number:

```{code-cell} ipython3
population.mean()
```

The maximum GDP:

```{code-cell} ipython3
countries['gdp_md_est'].max()
```

For dataframes, only the numeric columns are included in the result:

```{code-cell} ipython3
countries.median()
```

### Adding new columns

We can add a new column to a DataFrame with similar syntax as selecting a columns: create a new column by assigning the output to the DataFrame with a new column name in between the `[]`.

For example, to add the GDP per capita calculated above, we can do:

```{code-cell} ipython3
countries['gdp_capita'] = countries['gdp_md_est'] / countries['pop_est']
```

```{code-cell} ipython3
countries.head()
```

## Indexing: selecting a subset of the data

+++

### Subset variables (columns)

+++

For a DataFrame, basic indexing selects the columns (cfr. the dictionaries of pure python)

Selecting a **single column**:

```{code-cell} ipython3
countries['pop_est'] # single []
```

Remember that the same syntax can also be used to *add* a new columns: `df['new'] = ...`.

We can also select **multiple columns** by passing a list of column names into `[]`:

```{code-cell} ipython3
countries[['name', 'pop_est']] # double [[]]
```

### Subset observations (rows)

+++

Using `[]`, slicing or boolean indexing accesses the **rows**:

+++

### Slicing

```{code-cell} ipython3
countries[0:4]
```

### Boolean indexing (filtering)

+++

Often, you want to select rows based on a certain condition. This can be done with *'boolean indexing'* (like a where clause in SQL). 

The indexer (or boolean mask) should be 1-dimensional and the same length as the thing being indexed.

```{code-cell} ipython3
# taking the first 5 rows to illustrate
df = countries.head()
df
```

```{code-cell} ipython3
mask = df['pop_est'] > 1_000_000
mask
```

```{code-cell} ipython3
df[mask]
```

```{code-cell} ipython3
# or in one go
df[df['pop_est'] > 1_000_000]
```

With the full dataset:

```{code-cell} ipython3
countries[countries['gdp_md_est'] > 5_000_000]
```

```{code-cell} ipython3
countries[countries['continent'] == "Oceania"]
```

An overview of the possible comparison operations:

Operator   |  Description
------ | --------
==       | Equal
!=       | Not equal
\>       | Greater than
\>=       | Greater than or equal
<       | Lesser than
<=       | Lesser than or equal

and to combine multiple conditions:

Operator   |  Description
------ | --------
&       | And (`cond1 & cond2`)
\|       | Or (`cond1 \| cond2`)

+++

<div class="alert alert-info" style="font-size:120%">
<b>REMEMBER</b>: <br><br>

So as a summary, `[]` provides the following convenience shortcuts:

* **Series**: selecting a **label**: `s[label]`
* **DataFrame**: selecting a single or multiple **columns**:`df['col']` or `df[['col1', 'col2']]`
* **DataFrame**: slicing or filtering the **rows**: `df['row_label1':'row_label2']` or `df[mask]`

</div>

+++

## Let's practice! (part I)

Throughout the exercises in this course on vector data, we will work with several datasets about the city of Paris.

Here, we start with the following datasets:

- Information about the administrative districts of Paris: `paris_districts.csv`
- Real-time (at the moment I downloaded them ..) information about the public bicycle sharing system in Paris (vélib, https://opendata.paris.fr/explore/dataset/stations-velib-disponibilites-en-temps-reel/information/): `paris_bike_stations.csv`

+++

<div class="alert alert-success">

**EXERCISE**:

* Read the `data/paris_districts.csv` file, and assign the DataFrame to a variable called `districts`.
* Check the first rows of the DataFrame. 

<details>
  <summary>Hints</summary>

* For reading a CSV file, we can use the `pd.read_csv()` function. The first argument it takes is the path to the file.

</details>
    
</div>

+++

test

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts = pd.read_csv("data/paris_districts.csv")
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts.head()
```

<div class="alert alert-success">

**EXERCISE**:

* What is the average population number of the districts?
* And what is the median?

<details>
  <summary>Hints</summary>

* The average of a column can be calculated with the `mean()` method.
* Selecting a single column uses the "square bracket" notation `df['colname']`.

</details>
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts['population']
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts['population'].mean()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts['population'].median()
```

<div class="alert alert-success">

**EXERCISE**:

* What is the maximum area of the districts?
* The area column is expressed in m². What is the maximum area in km² ?
* And can you also calculate in the area in km² for the full column?

<details>
  <summary>Hints</summary>

* The maximum of a column can be calculated with the `max()` method.
* The division operator is `/`, and if we want to take the power of 2 we can use `10**2` (so not `10^2` as you might expect from other languages!).
* Operations on a Series are *element-wise*. For example, to add a number to each element of the Series `s`, we can do `s + 2`.
    
</details>
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts['area'].max()
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts['area'].max() / 1000**2  # or / 10**6
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts['area'] / 1000**2
```

<div class="alert alert-success">

**EXERCISE**:

* Calculate the population density for all districts, expressed in "inhabitant / km²". Call the resulting Series `population_density`.
* What is the maximum population density?

<details>
  <summary>Hints</summary>

* Dividing two Series objects also works element-wise: the first element of Series 1 divided by the first element of Series 2, the second by the second, etc.

</details>
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

population_density = districts["population"] / (districts["area"] / 1000**2)
population_density
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

population_density.max()
```

<div class="alert alert-success">

**EXERCISE**:

* Add the population density as a new column to the `districts` dataframe.

<details>
  <summary>Hints</summary>

* Adding a column to a DataFrame uses similar syntax as selecting one with `[]`. But now we assign values to that column: `df["new_colum"] = values`

</details>
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts['population_density'] = districts["population"] / (districts["area"] / 1000**2)
districts.head()
```

<div class="alert alert-success">

**EXERCISE**:

* Sort the `districts` DataFrame by the population number. Sort in such a way that the districts with the largest population are at the top of the DataFrame (Tip: check the help of the function!)

<details>
  <summary>Hints</summary>

* Sorting values of a Series, of the rows of a DataFrame, can be done with the `sort_values` method.
* For sorting a DataFrame by a certain column, specify the column name with the `by=` keyword.
* The `ascending` keyword determines if the largest values are sorted at the bottom or at the top of the DataFrame.
</details>
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts.sort_values(by="population", ascending=False)
```

<div class="alert alert-success">

**EXERCISE**:

* Select all rows for the districts of the 3rd arrondissement.
* For this subset, what is the total population of the arrondissement?
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

arr3 = districts[districts["arrondissement"] == 3]
arr3
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

arr3["population"].sum()
```

<div class="alert alert-success">

**EXERCISE**:

* Select the districts with a population of more than 50.000 inhabitants.

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts[districts['population'] > 50000]
```

<div class="alert alert-success">

**EXERCISE**:

* How many districts have a population of more than 50.000 inhabitants?

<details>
  <summary>Hints</summary>

* The number of rows of a DataFrame can be obtained with the `len()` function (not a method!). Or alternatively with the `shape` attribute.
* Alternatively, we can also get this number based on the *condition*: counting the number of True values is the same as taking the sum of this condition.
</details>
    
</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

subset = districts[districts['population'] > 50000]
len(subset)
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

subset.shape
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

(districts['population'] > 50000).sum()
```

## Plotting: visual exploration of data

+++

The **`plot`** method can be used to quickly visualize the data in different ways:

```{code-cell} ipython3
countries['pop_est'].plot();
```

The default is a *line* plot. However, for this dataset, that's a not very useful plot type. With the `kind` keyword, you can specify other plot types:

```{code-cell} ipython3
countries['pop_est'].plot(kind='hist')
```

This is still not the best plot. This is due to a few countries with a very large population.

+++

### A `matplotlib` primer

The plot produced by pandas with the `.plot()` method, is actually created using the `matplotlib` package.

[Matplotlib](http://matplotlib.org/) is a Python package used widely throughout the scientific Python community to produce high quality 2D publication graphics. It transparently supports a wide range of output formats including PNG (and other raster formats), PostScript/EPS, PDF and SVG and has interfaces for all of the major desktop GUI (graphical user interface) toolkits. It is a great package with lots of options.

However, matplotlib is is also a *huge* library, with which you can plot anything you want and customize every detail of the plot ... if you know how to do this. 

So in this course, we are mostly going to use matplotlib through a convenience layer, such as the pandas `.plot()` method, or a helper library like `seaborn`. But you'll some basic matplotlib techniques as well.

+++

Matplotlib comes with a convenience sub-package called ``pyplot`` which, for consistency with the wider matplotlib community, should always be imported as ``plt``:

```{code-cell} ipython3
import matplotlib.pyplot as plt
```

The object returned by the pandas `plot()` method is called an **Axes**

```{code-cell} ipython3
ax = countries['pop_est'].plot(kind='hist')
```

```{code-cell} ipython3
type(ax)
```

The Axes represents the "data space" of a typical plot: where data is being plotted, and typically having an x and y *axis*. The Axes is part of a **Figure** (in the above, the Figure has one Axes, or subplot, but you can also create a Figure with multiple Axes or subplots). 

We can also create this Figure and Axes manually:

```{code-cell} ipython3
fig, axs = plt.subplots()  # ncols=
```

and then specify the Axes to plot on with pandas:

```{code-cell} ipython3
fig, axs = plt.subplots()
countries['pop_est'].plot(kind="hist", ax=axs)
```

The Axes object can then be used for further customization:

```{code-cell} ipython3
fig, axs = plt.subplots()
countries['pop_est'].plot(kind="hist", ax=axs, bins=50)
axs.set_title("Countries of the world")
axs.set_xlabel("Population")
axs.set_xlim(0, 5e8)
```

An example of another package built on top of matplotlib is **`seaborn`** (https://seaborn.pydata.org/). It provides a high-level interface for a set of statistical graphics.

For example, we can make a boxplot of the GDP per capita for each continent:

```{code-cell} ipython3
import seaborn
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(8, 8))
seaborn.boxplot(y="continent", x="gdp_capita", color="C0", data=countries, ax=ax)  # violinplot
```

This is only an ultra short intro to matplotlib. In the course materials, you can find another notebook with some more details ([visualization-01-matplotlib.ipynb](visualization-01-matplotlib.ipynb#An-small-cheat-sheet-reference-for-some-common-elements)).

+++

<div class="alert alert-info" style="font-size:18px">

**Galleries!**

Galleries are great to get inspiration, see the plot you want, and check the code how it is created:
    
* [matplotlib gallery](http://matplotlib.org/gallery.html) is an important resource to start from
* [seaborn gallery](https://seaborn.pydata.org/examples/index.html)
* The Python Graph Gallery (https://python-graph-gallery.com/)

</div>

+++

## Aggregating statistics grouped by category

<img align="center" src="../img/pandas/06_groupby1.svg">

+++

Assume we want to know the total population number of a certain continent. Using the boolean indexing and aggregation we learned above, we can do:

```{code-cell} ipython3
africa = countries[countries['continent'] == "Africa"]
```

```{code-cell} ipython3
africa['pop_est'].sum()
```

To calculate this for all continents, we could repeat the above for each continent. However, this quickly becomes tedious, and can directly be performed by pandas:

```{code-cell} ipython3
countries.groupby('continent')['pop_est'].sum()
```

Calculating a given statistic (e.g. sum of the population) for each category in a column (e.g. the different continents) is a common pattern. The `groupby()` method is used to support this type of operations. More general, this fits in the more general split-apply-combine pattern:

* **Split** the data into groups
* **Apply** a function to each group independently
* **Combine** the results into a data structure

The apply and combine steps are typically done together in pandas.

```{code-cell} ipython3
countries.groupby('continent')['pop_est'].sum().plot(kind="barh")
```

## Let's practice! (part II)

```{code-cell} ipython3
districts = pd.read_csv("data/paris_districts.csv")
stations = pd.read_csv("data/paris_bike_stations.csv")
```

```{code-cell} ipython3
districts.head()
```

```{code-cell} ipython3
stations.head()
```

<div class="alert alert-success">
<b>EXERCISE</b>:

* Plot the population distribution of the Paris districts

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts['population'].hist()  # or .plot(kind="hist")
```

<div class="alert alert-success">

<b>EXERCISE</b>:

* Using groupby(), calculate the total population of each of the arrondissements.

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

districts.groupby('arrondissement')['population'].sum()
```

<div class="alert alert-success">

<b>EXERCISE</b>:

* Using the bike stations dataset (`stations`), make a figure with a histogram of the total bike stands and available bikes.

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

fig, ax = plt.subplots()
stations["bike_stands"].hist(ax=ax, alpha=.5, label="Total bike stands")
stations["available_bikes"].hist(ax=ax, alpha=.5, label="Available bikes")
ax.legend()
```

<div class="alert alert-success">

<b>EXERCISE</b>:

* Using `seaborn`, make a boxplot of the number of bike stands (in the `stations` dataframe) per arrondissement.

</div>

```{code-cell} ipython3
:tags: [nbtutor-solution]

import seaborn
```

```{code-cell} ipython3
:tags: [nbtutor-solution]

seaborn.boxplot(x="arrondissement", y="bike_stands", data=stations)
```

## Other useful things to know!

This notebook is only an intro. The pandas library provides a lot more functionality for working with tabular data, which we won't be cover in this course.

+++

### Counting values

+++

Do you want to know what the unique values are of a column, and how many times each value occurs? Use the `value_counts()` method:

```{code-cell} ipython3
countries['continent'].value_counts()
```

### Selecting a specific value of the DataFrame

+++

To access a specific value of a DataFrame, we can use the `.loc` method passing the (row label, column name):

```{code-cell} ipython3
countries.loc[0, "name"]
```

### Merging two dataframes

+++

Pandas provides several ways to combine different DataFrames. If there is a common column on which you want to match both DataFrames, we can use the `pd.merge()` function:

```{code-cell} ipython3
cities = pd.read_csv("data/cities.csv")
```

```{code-cell} ipython3
cities.head()
```

```{code-cell} ipython3
countries.head()
```

Both DataFrames have the `'iso_a3'` column with a 3-character code of the country. Based on this, we can add information about the country to the cities dataset:

```{code-cell} ipython3
pd.merge(cities, countries, on="iso_a3")
```

## Towards geospatial data

The datasets used in this notebook are containing spatial information: data about areas (countries, districts) or point locations (cities, bike stations). But the data itself didn't always explicitly include the the spatial component. For example, we don't know the exact extent of the countries with the dataset used here. 

With point locations, such as the cities DataFrame, the location is included as two columns:

```{code-cell} ipython3
cities.head()
```

Which allows us to, for example, plot the locations manually:

```{code-cell} ipython3
cities.plot(x="longitude", y="latitude", kind="scatter")
```

However, this doesn't enable to *easily* work with those locations and do spatial analyses on them. For that, we are going to introduce a new package: **`geopandas`**.

As illustration, we convert the pandas DataFrame with cities into a geopandas GeoDataFrame:

```{code-cell} ipython3
import geopandas
```

```{code-cell} ipython3
cities_geo = geopandas.GeoDataFrame(cities, geometry=geopandas.points_from_xy(cities["longitude"], cities["latitude"]))
```

```{code-cell} ipython3
cities_geo
```

Now, we have a single column with the location information (the "geometry" column). This is the topic of the next notebook.
