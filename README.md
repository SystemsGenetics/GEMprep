# GEM_PREP

Hi Rachel.  This repo conatins code for preprocessing Gene Expression Matrices (GEMs).  Here are the eventual functionalities.  Let's get them working individually and then we can write a python wrapper or NextFlow workflow!

Check out NextFlow:  https://www.nextflow.io/
The GEMmaker worflow is built on NextFlow: https://github.com/SystemsGenetics/GEMmaker

 
PREPROCESS 
(outlier_removal, normalize_quantile)  --- Benafsh has this code

CLUSTER --- Iris/Will know how to run tSNE.  This is Kim's code for tSNE/HDBSCAN:  https://github.com/feltus/tSNE_HDBSCAN
(tSNE, OTHER CLUSTERING METHODS)

VISUALIZE 
(heatmap, histogram - before/after preprocessing)

REPORT
(How many outliers removed; Average gene expression + stddev)

SPLIT_INTO_SUBGEMS 
(based on a sample list)


