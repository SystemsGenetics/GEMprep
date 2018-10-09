# GEMprep

This repository contains a variety of tools for gene expression matrices (GEMs). These tools include:

- Normalization: log2 transform, KS-test outlier removal, quantile normalization
- Visualization: t-SNE, sample distributions

TODO: Included is a Nextflow workflow which provides a single interface through which to use the GEMprep tools:

![image](https://user-images.githubusercontent.com/26093060/45060839-c2bfac80-b06f-11e8-8850-90a4bb0f9113.png)

This repository is designed for use on Clemson University's Palmetto Cluster. Documentation for the Palmetto Cluster can be found [here](https://www.palmetto.clemson.edu/palmetto/).

## Prerequisites

The recommended way to use the scripts in this repository is with an Anaconda environment. To create an Anaconda environment:
```
module add anaconda3/5.1.0

conda create -n myenv python=3.6
```

From here you can activate your environment and install any necessary packages for Python and R:
```
source activate myenv

conda install matplotlib numpy pandas seaborn
conda install r

source deactivate
```

To use the Nextflow workflow, you must first install Nextflow:
```
module add java/1.8.0

curl -s https://get.nextflow.io | bash

./nextflow run hello
```

## Tools

### Normalize

To normalize an FPKM expression matrix, use the `normalize.R` script:
```
Rscript scripts/normalize.R
```

This script expects an input file called `FPKM.txt` and performs log2 transform, KS test outlier removal, and quantile normalization. It produces a normalized matrix file called `GEM.txt` as well as a log file of the KS test results and several visualizations.

### Visualize

TODO

