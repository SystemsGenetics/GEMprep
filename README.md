# GEMprep

This repository contains a variety of tools for gene expression matrices (GEMs). These tools can be used individually or through a [Nextflow](https://nextflow.io/) pipeline, also provided in this repository:

<img src="images/pipeline.png"/>

## Dependencies

The recommended way to use the scripts in this repository is with an Anaconda environment. To create an Anaconda environment:
```bash
module add anaconda3/5.1.0

conda create -n gemprep python=3.6 matplotlib mpi4py numpy pandas r scikit-learn seaborn
```

Once this environment has been created, the R package `preprocessCore` must be seperately installed:

```bash
source activate gemprep

# open a shell in R
R

> install.packages("BiocManager")
> BiocManager::install()
> BiocManager::install(c("preprocessCore"))
```

To use the Nextflow pipeline, you must first install Nextflow:
```bash
module add java/1.8.0

curl -s https://get.nextflow.io | bash

./nextflow run hello
```

## Usage

__NOTE__: For any of the Python scripts described below, you can run the script with the `-h` option to see all of the available options.

### Nextflow

The Nextflow pipeline can run several tools on a set of GEM files in a single run using the scripts in the `bin` folder. By default, the pipeline uses all GEM files in the `input` directory, runs all steps that are enabled in `nextflow.config`, and saves all results to the `output` folder. There are several settings, such as the directory to your conda environment and the steps to run, which can be found in the `params` section of `nextflow.config`. These settings can be modified to fit the user's needs.

To run the Nextflow pipeline:
```bash
# place input files in the input directory
mkdir input
# ...

nextflow run main.nf
```

### Plaintext and Binary formats

The primary way to store an expression matrix in a file is as a tab-delimited text file which includes the row names and column names. The same matrix can also be stored as a binary Numpy (`.npy`) file, which includes only the data, and separate text files for the row names and column names. The script `convert.py` can convert expression matrix files between these two formats:
```bash
# convert an expression matrix from plaintext to binary
python bin/convert.py GEM.txt GEM.npy

# convert the binary matrix back to plaintext
python bin/convert.py GEM.npy GEM.txt
```

Every Python script in this repository can load and save expression matrices using either format, depending on whether you provide `txt` or `npy` file arguments.

### Normalize

To normalize an expression matrix, there are two scripts, `normalize.py` and `normalize.R`. Both scripts have the same functionality. The Python script is easier to use and can use MPI for the K-S test, but it's implementation of quantile normalization does not exactly match the R implementation.

To use the `normalize.py` script:
```bash
python bin/normalize.py <infile> <outfile> [options]
```

To use the `normalize.R` script:
```bash
Rscript bin/normalize.R [--log2] [--kstest] [--quantile]
```

This script expects an input file called `FPKM.txt` and performs log2 transform, KS test outlier removal, and quantile normalization. It produces a normalized matrix file called `GEM.txt` as well as a log file of the KS test results and several visualizations.

There is also a script, `normalize-frankenstein.pbs` that combines these two scripts in a pbs job submission, performing the K-S test and outlier removal using `normalize.py` and then performs quantile normalization using `normalize.R`. This script should be edited to provide the path to the input file as well as both the R and python normalizatin scripts. It expects an input in the form of `<dataset>_FPKM.txt` and outputs the GEM as `<dataset>.emx.txt`.

### Visualize

To create visualizations of an expression matrix, use the `visualize.py` script:
```bash
python bin/visualize.py <infile> [options]
```

This script takes an expression matrix file (which may or may not be normalized) and creates several visualizations based on the command line arguments that you provide. Currently this script supports two visualizations:

- Density plot: plot the distribution of each sample
- t-SNE plot: plot the t-SNE of all samples

For an unnormalized matrix, the sample distributions will vary greatly, but for a normalized matrix, the samples should have similar distributions. For the t-SNE plot, a label file can be provided to color the data points by their respective label. The file should contain a label for each sample, separated by newlines. The labels can be text or numeric.

### Partitioning

To partition an expression matrix into several sub-matrices, use the `partition.py` script:
```bash
# use a pre-defined partition file
python bin/partition.py <infile> --partitions [partition-file]

# use an automatic partitioning scheme with N partitions
python bin/partition.py <infile> --n-partitions N
```

This script takes an expression matrix and creates several submatrices based on a partitioning scheme. You can either provide a custom partition file or use the script to automatically generate partitions. The partition file should have two columns, the first column being sample names and the second column being partition labels. When generating partitions automatically, the script will output the resulting partition file, which you can modify to create your own partition files. Run with `-h` to see the list of available options.

### Merging

To merge several expression matrices into a single matrix, use the `merge.py` script:
```bash
python bin/merge.py <infiles> <outfile>
```
