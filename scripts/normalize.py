import argparse
import mpi4py.MPI as MPI
import numpy as np
import pandas as pd
import scipy.stats
import sklearn.preprocessing

# initialize MPI parameters
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()



def transform_log2(X):
	# transform each column
	for i in range(X.shape[1]):
		if rank == i % size:
			X[:, i] = np.log2(X[:, i])

	# gather columns
	requests = []

	for i in range(X.shape[1]):
		source = i % size

		if source == 0:
			continue

		if rank == 0:
			requests.append(comm.Irecv(X[:, i], source=source))
		elif rank == source:
			requests.append(comm.Isend(X[:, i], dest=0))

	for req in requests:
		req.wait()

	# broadcast transformed matrix
	comm.Bcast(X, root=0)



def transform_kstest(X):
	# extract global distribution
	g = X.reshape(-1)
	g = g[~np.isnan(g)]
	g = scipy.stats.norm.cdf(g)

	print("%d: extracted global distribution: %s" % (rank, str(g.shape)))

	# perform K-S test on each column
	ks_results = []

	for i in range(X.shape[1]):
		if rank == i % size:
			# extract column
			x_i = X[:, i]
			x_i = x_i[~np.isnan(x_i)]
			x_i = scipy.stats.norm.cdf(x_i)

			# perform K-S test between column and global distribution
			d, p = scipy.stats.mstats.ks_twosamp(x_i, g)

			# save results
			ks_results.append((i, d, p))

	# gather results from K-S test
	ks_results = comm.reduce(ks_results, op=MPI.SUM, root=0)

	# save results to file
	if rank == 0:
		ks_results.sort()

		file = open("ks-results.txt", "w")
		file.write("\n".join([("%3d %8.3f %8.3f" % t) for t in ks_results]))

	# TODO: remove outliers (d > 0.15)



def transform_quantile(X):
	# TODO: review quantile_transform() documention

	if rank == 0:
		sklearn.preprocessing.quantile_transform(X, copy=False)



if __name__ == "__main__":
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", required=True, help="input expression matrix", dest="INPUT")
	parser.add_argument("-o", "--output", required=True, help="output expression matrix", dest="OUTPUT")
	parser.add_argument("--log2", action="store_true", help="whether to perform a log2 transform", dest="LOG2")
	parser.add_argument("--kstest", action="store_true", help="whether to perform outlier removal using the K-S test", dest="KSTEST")
	# TODO: --kstest-dropna
	# TODO: --kstest-threshold
	parser.add_argument("--quantile", action="store_true", help="whether to perform quantile normalization", dest="QUANTILE")

	args = parser.parse_args()

	# load input matrix into dataframe
	emx = pd.read_table(args.INPUT, index_col=0, na_values=0)

	# extract column-major numpy array from dataframe
	X = np.array(emx.values, order="F")

	print("%d: loaded expression matrix: %s" % (rank, str(emx.shape)))

	# perform log2 transform
	if args.LOG2:
		transform_log2(X)

	# perform K-S test
	if args.KSTEST:
		transform_kstest(X)

	# perform quantile normalization
	if args.QUANTILE:
		transform_quantile(X)

	# save output matrix
	if rank == 0:
		emx.iloc[:] = X
		emx.to_csv(args.OUTPUT, sep="\t", na_rep="NA", float_format="%.8f")
