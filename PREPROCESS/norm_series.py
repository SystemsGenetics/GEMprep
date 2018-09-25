import numpy as np
import pandas as pd
import scipy
data = pd.read_table('/zfs/feltus/bhusain/panTCGA-FPKM-GEM.txt', na_values=0)
rows = list(data.iloc[:,0])
cols = list(data.columns)[1:]
array = data.values[:,1:]
#print('Row:# %d, Cols: # %d ' % (len(rows), len(cols)))
#print('Array: ', array.shape)

origarray = np.array(array,dtype=np.float64)
prematrix = np.log2(origarray).round(13)

g = prematrix[:,0]

for i in range(1, len(cols)):
    g= np.append(g,prematrix[:,i])
#print(g.shape)
no_norm_g = g[~np.isnan(g)]



from scipy.stats.mstats import ks_2samp as ks_2sampm
from scipy.stats import norm as norm
ks_test = []
for i in range(len(cols)):
    array = prematrix[:,i]
    no_norm_a = array[~np.isnan(array)]
    d,p = ks_2sampm(norm.cdf(no_norm_a),  norm.cdf(no_norm_g))
    #print(cols[i],d,p)
    if d < 0.15:
        ks_test.append(cols[i])

#print("Non Outliers : %d, Outliers :%d" % (len(ks_test),len(cols)-len(ks_test)))

import scipy.stats as sts
'''
    def quantile_normalize(dataframe, cols, pandas=pd):
    
    # copy dataframe and only use the columns with numerical values
    #df = dataframe.copy().filter(items=cols)
    df = dataframe
    
    zerodf = df.fillna(0)
    # columns from the original dataframe not specified in cols
    non_numeric = dataframe.filter(items=list(filter(lambda col: col not in cols, list(dataframe))))
    
    print("DF:",df.shape)
    rank_mean = zerodf.stack().groupby(zerodf.rank(method='first').stack()).mean()
    
    print("Rank Mean", rank_mean.shape)
    norm = zerodf.rank(method='min').stack().astype(int).map(rank_mean).unstack()
    
    
    result = pandas.concat([norm, non_numeric], axis=1)
    #return result
    return norm
    '''


def quantileNormalize(df_input):
    df = df_input.copy()
    df = df.fillna(0)
    #compute rank
    dic = {}
    for col in df:
        dic.update({col : sorted(df[col])})
    sorted_df = pd.DataFrame(dic)
    rank = sorted_df.mean(axis = 1,skipna=True).tolist()
    #rank2 = sorted_df.mean(axis = 1).tolist()
    #print(rank)
    #sort
    for col in df:
        t = np.searchsorted(np.sort(df[col]), df[col])
        df[col] = [rank[i]  for i in t]
        df[col] = np.where(np.isnan(df_input[col]), df_input[col], df[col])
    
    
    return df



newdata = pd.DataFrame(data=prematrix, columns = cols)[ks_test]
#ks_test
#quantile_normalize(newdata, cols=ks_test)
nmatrix=quantileNormalize(newdata)
#newdata=newdata.fillna(0)
#newdata.fillna(0).stack(dropna=False).groupby(newdata.rank(method='first').stack(dropna=False).fillna(0)).mean().shape

#from sklearn.preprocessing import quantile_transform
#print(nmatrix)

idx = 0
s = data.ix[:,0]
#print(s)
nmatrix.insert(loc=idx,column = '',value=s)

#nmatrix.drop(nmatrix.columns[1], axis=1, inplace=True)
nmatrix.to_csv('/zfs/feltus/bhusain/normalized_test.txt', sep='\t')
