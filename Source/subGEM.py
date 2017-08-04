"""
subGEM.py
Created 8/3/17
William Poehlman <wpoehlm@clemson.edu>
Available under GPL-2.0

This script requires two arguments:

1. Input gene expression matrix(GEM): tab delimited file with a sample header
2. SampleID-ClusterID mapping table: Tab delimited.  First column is sample ID, second column is cluster ID

Ouput:  tab delimited GEMs containing only the specific samples found in each cluster

Software requirements:

Python Pandas module 

On the Palmetto cluster, you can load module 'anaconda/4.2.0'

For example:

qsub -I
module load anaconda/4.2.0

python subGEM.py test.tab cluster_sample_map.txt

"""

import sys
import pandas as pd


matrix = sys.argv[1]
clumap = sys.argv[2]
clusterset = set()
dict = {}


# load GEM into pandas data frame
matrixdf = pd.read_table(matrix)

# create dictionary where clusterIDs are keys and list of sampleIDs are values
for line in open(clumap):
    cluster = line.strip().split('\t')[1]
    sample = line.strip().split('\t')[0]
    clusterset.add(cluster)
    
    if cluster not in dict:
        dict[cluster] = [sample]
    else:
        dict[cluster].append(sample)


# extract sample subsets for each cluster and write sub-GEM files
for item in clusterset:
    subsamp = dict[item]
    subgem = matrixdf[subsamp]
    outname = str(item + '_subGEM.tab')
    subgem.to_csv(outname,sep='\t')




