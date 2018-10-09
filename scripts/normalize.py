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
	for i in range(X.shape[1]):
		root = i % size
		comm.Bcast(X[:, i], root=root)



def transform_kstest(X, keepna=False, threshold=0.15, logfile=None):
	# extract global distribution
	g = X.reshape(-1, order="F")
	if not keepna:
		g = g[~np.isnan(g)]
	# g = scipy.stats.norm.cdf(g)

	print("%d: extracted global distribution: %s" % (rank, str(g.shape)))

	# perform K-S test on each column
	ks_results = []

	for i in range(X.shape[1]):
		if rank == i % size:
			# extract column
			x_i = X[:, i]
			if not keepna:
				x_i = x_i[~np.isnan(x_i)]
			# x_i = scipy.stats.norm.cdf(x_i)

			# perform K-S test between column and global distribution
			d, p = scipy.stats.mstats.ks_twosamp(x_i, g)

			# save results
			ks_results.append((i, d, p))

	# gather results from K-S test
	ks_results = comm.reduce(ks_results, op=MPI.SUM, root=0)

	if rank != 0:
		return None

	# sort results by column index
	ks_results.sort()

	# save results to file
	if logfile != None:
		file = open(logfile, "w")
		file.write("\n".join([("%12.6f %12.6f" % (d, p)) for (_, d, p) in ks_results]))

	# return mask of non-outliers
	return [d < threshold for (_, d, p) in ks_results]



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
	parser.add_argument("--ks-log", help="log file of K-S test results", dest="KS_LOG")
	parser.add_argument("--ks-keepna", action="store_true", help="whether to keep nan's during K-S test", dest="KS_KEEPNA")
	parser.add_argument("--ks-threshold", type=float, default=0.15, help="threshold for K-S test", dest="KS_THRESHOLD")
	parser.add_argument("--quantile", action="store_true", help="whether to perform quantile normalization", dest="QUANTILE")

	args = parser.parse_args()

	# load input matrix as numpy array
	X = np.load(args.INPUT)
	X[X == 0] = np.nan

	print("%d: loaded expression matrix: %s" % (rank, str(X.shape)))

	# load row names and column names
	BASENAME = ".".join(args.INPUT.split(".")[:-1])

	rownames = np.loadtxt("%s_rownames.txt" % BASENAME, dtype=str)
	colnames = np.loadtxt("%s_colnames.txt" % BASENAME, dtype=str)

	# perform log2 transform
	if args.LOG2:
		transform_log2(X)

	# perform K-S test
	if args.KSTEST:
		mask = transform_kstest(X, keepna=args.KS_KEEPNA, threshold=args.KS_THRESHOLD, logfile=args.KS_LOG)

		# remove outliers from FPKM matrix
		if rank == 0:
			X = X[:, mask]
			colnames = colnames[mask]

	# perform quantile normalization
	if args.QUANTILE:
		mask = transform_quantile(X)

	# save output matrix
	if rank == 0:
		emx = pd.DataFrame(X, index=rownames, columns=colnames)
		emx.to_csv(args.OUTPUT, sep="\t", na_rep="NA", float_format="%.8f")
