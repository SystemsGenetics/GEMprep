# GEM_PREP

The GEM_PREP repository contains code for preprocessing Gene Expression Matrices (GEMs).  Included is a NextFlow workflow to perform the functionalities included in the following flowchart.  The process receives a GEM as a .fpkm file, and returns a GEM that is ready for processing.

The files in this repository are designed for use on Clemson University's Palmetto Cluster.  Included below is the Palmetto Cluster User Guide.
https://www.palmetto.clemson.edu/palmetto/userguide_basic_usage.html

![image](https://user-images.githubusercontent.com/26093060/45060839-c2bfac80-b06f-11e8-8850-90a4bb0f9113.png)

## Prerequisites

Python2
NextFlow
Java v8
R
Anaconda
Pandas
GEM (Gene Expression Matrix)

## Visualize

TODO

## Preprocess

There are two options for preprocessing.  Preprocessing includes a log transform, outlier removal using the CDF test, quantile normalization, and the KS test.  The scripts are run in parallel or in series.
  Series - This code includes all portions of the preprocessing section, meaning log transform, outlier removal using the CDF test, quantile normalization, and the KS test.
   norm_series.py
   norm_series.pbs
  Parallel - This code includes the portions of the preprocessing section except quantile normalization, which is still in development.  Therefore, the parallel code include log transform, outlier removal using the CDF test, quantile normalization, and the KS test.
