# Python for GIS and Geoscience

This repo contains the source code for the workshop (the notebooks with full
content) as it is being developed. For the actual course repo, see for
example [DS-python-geospatial](https://github.com/jorisvandenbossche/DS-python-geospatial).

## Introduction

An important aspect of daily work in geographic information science and earth sciences is the handling of potentially large amounts of data. Reading in spatial data, exploring the data, creating visualisations and preparing the data for further analysis may become tedious tasks. Hence, increasing efficiency and reproducibility in this process without the need of a GUI interface is beneficial for many scientists. The usage of high-level scripting languages such as R and Python are increasingly popular for these tasks thanks to the development of GIS oriented packages.

This course trains students to use Python effectively to do these tasks, with a focus on geospatial data. It covers both vector and raster data. The course focuses on introducing the main Python packages for handling such data (GeoPandas, Numpy and Rasterio, Xarray) and how to use those packages for importing, exploring, visualizing and manipulating geospatial data. It is the aim to give the students an understanding of the data structures used in Python to represent geospatial data (geospatial dataframes, (multi-dimensional) arrays and composite netCDF-like multi-dimensional datasets), while also providing pointers to the broader ecosystem of Python packages for GIS and geosciences.

The course has been developed as a specialist course for the Doctoral schools of Ghent University, but can be taught to others upon request.

## Aim & scope

This course targets researchers that want to enhance their general data manipulation and analysis skills in Python specifically for handling geospatial data.

The course does not aim to provide a course in specific spatial analysis and statistics, cartography, remote sensing, OGC web services, ... or general Geographical Information Management (GIS). It aims to provide researchers the means to effectively tackle commonly encountered spatial data handling tasks in order to increase the overall efficiency of the research. The course does not tackle desktop GIS Python extensions such as arcpy or pyqgis.

## Getting started

The course uses Python 3, data analysis packages such as Pandas, Numpy and Matplotlib and geospatial packages such as GeoPandas, Rasterio and Xarray. To install the required libraries, we highly recommend Anaconda or miniconda (<https://www.anaconda.com/download/>) or another Python distribution that includes the scientific libraries (this recommendation applies to all platforms, so for both Window, Linux and Mac).

For detailed instructions to get started on your local machine , see the [setup instructions](./setup.md).

In case you do not want to install everything and just want to try out the course material, use the environment setup by Binder [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/jorisvandenbossche/course-python-geospatial/HEAD?urlpath=lab/tree/notebooks ) and open de notebooks rightaway.


## Contributing

Found any typo or have a suggestion, see [how to contribute](./CONTRIBUTING.md).

## Development

In addition to the environment.yml, install the following packages:

```
conda install jupytext jlab-enhanced-cell-toolbar nbdime
```

Creating the student version materials from this repo:

```
export COURSE_DIR="DS-python-geospatial-2022"

git clone https://github.com/jorisvandenbossche/DS-python-geospatial.git $COURSE_DIR
git clone https://github.com/jorisvandenbossche/course-python-geospatial.git course-python-geospatial-clean

cp course-python-geospatial-clean/notebooks/*.ipynb $COURSE_DIR/_solved/
cp course-python-geospatial-clean/notebooks/data/ $COURSE_DIR/notebooks/ -r
cp course-python-geospatial-clean/img/ $COURSE_DIR/ -r
cp course-python-geospatial-clean/environment.yml $COURSE_DIR/
cp course-python-geospatial-clean/check_environment.py $COURSE_DIR/
cd $COURSE_DIR/
./convert_notebooks.sh
jupyter nbconvert --clear-output _solved/*.ipynb
```


## Meta
Authors: Joris Van den Bossche, Stijn Van Hoey
