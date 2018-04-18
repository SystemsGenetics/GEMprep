# Quantile Normalization
# quantileNormalization.py
# Rachel Eimen
# 4/6/18
# Description:  Reads in and quantile normalizes a matrix.  It returns the normalized matrix in a file titled "output.txt".

import pandas as pd
import numpy as np
import math

data = pd.read_csv('panTCGA-HTSEQ-GEM.txt.gz',sep='\t')

dic = {}

for col in data:
    dic.update({col : sorted(data[col])})

sorted_df = pd.DataFrame(dic, dtype = np.float32)
rank = sorted_df.mean(axis = 1).tolist()

for col in data:
    t = np.searchsorted(np.sort(data[col]), data[col])
    data[col] = [rank[i] for i in t]

with open('output.txt', 'w') as file:
    file.write(data.to_string())

