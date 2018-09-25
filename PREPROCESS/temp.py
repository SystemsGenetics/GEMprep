import numpy as np
import pandas as pd
import scipy
from multiprocessing import Pool, RawArray
from scipy.stats.mstats import ks_2samp 
from scipy.stats import norm as norm

data = pd.read_table('/zfs/feltus/bhusain/panTCGA-FPKM-GEM.txt', na_values=0)
rows = list(data.iloc[:,0])
cols = list(data.columns)[1:]
array = data.values[:,1:]
print ('Row:# %d, Cols: # %d ' % (len(rows), len(cols)))
print ('Array: ', array.shape)

num_processes = 12


origarray = np.array(array,dtype=np.float64)
prematrix = np.log2(origarray).round(13)

g = prematrix[:,0]

for i in range(1, len(cols)):
    g= np.append(g,prematrix[:,i])
print("G.Shape", g.shape)
g = np.array(g)
no_norm_g = g[~np.isnan(g)]

var_dict = {}

def init_worker(orig, orig_without_na, row_count):
    # Using a dictionary is not strictly necessary. You can also
    # use global variables.
    var_dict['orig'] = orig
    var_dict['orig_without_na'] = orig_without_na
    var_dict['row_count'] = row_count

 
def worker_func(i):
    # Simply computes the sum of the i-th row of the input matrix X
    count = var_dict['row_count']
    all_data = np.frombuffer(var_dict['orig_without_na'])
    subset =   np.frombuffer(var_dict['orig'])
    subset = subset[i*count: (i+1)*count]
    subset = subset[~np.isnan(subset)]

    d,p = ks_2samp(norm.cdf(subset), norm.cdf(all_data))
    #print(col[i],d,p)
    #if d < 0.15:
    return d, p
#return NULL

X=RawArray('d', no_norm_g.shape[0])
Y=RawArray('d', g.shape[0])
X_np = np.frombuffer(X).reshape(no_norm_g.shape)
Y_np = np.frombuffer(Y).reshape(g.shape)
np.copyto(X_np, no_norm_g)
np.copyto(Y_np, g)

pool =  Pool(processes=num_processes, initializer=init_worker, initargs=(g, no_norm_g, len(rows)))
result = pool.map(worker_func, range(len(cols)))
#print(result)

np.savetxt("/zfs/feltus/bhusain/test_norm.txt", result, delimiter='\t')
#for i in result:
#    print(i[0], i[1])
#print(np.array(result).sum(), len(cols)-(np.array(result).sum()))
