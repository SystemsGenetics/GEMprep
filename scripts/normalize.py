import argparse
import mpi4py.MPI as MPI
import numpy as np
import pandas as pd
import scipy.stats

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



def transform_kstest(X, colnames, keepna=False, threshold=0.15, logfile=None):
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
			ks_results.append((i, colnames[i], d, p))

	# gather results from K-S test
	ks_results = comm.reduce(ks_results, op=MPI.SUM, root=0)

	if rank != 0:
		return None

	# sort results by column index
	ks_results.sort()

	# save results to file
	if logfile != None:
		f = open(logfile, "w")
		f.write("%s\t%s\t%s\n" % ("sample", "d", "p"))
		f.write("\n".join([("%s\t%.6f\t%.6f" % (colname, d, p)) for (_, colname, d, p) in ks_results]))

	# return mask of non-outliers
	return [d < threshold for (_, _, d, p) in ks_results]



def transform_quantile(X):
	if rank != 0:
		return

	# compute map of nan values
	X_isnan = np.isnan(X)

	# compute argsort of each column
	X_argsort = np.empty_like(X, dtype=np.int32)

	for i in range(X.shape[1]):
		X_argsort[:, i] = np.argsort(X[:, i])

	# convert nan values to zeros temporarily
	X[X_isnan] = 0

	# compute mean of sorted columns
	# equivalent to np.nanmean(X_sorted, axis=1)
	mean = np.zeros(X.shape[0], dtype=X.dtype)
	counts = np.zeros(X.shape[0], dtype=np.int32)

	for i in range(X.shape[1]):
		mean += X[X_argsort[:, i], i]
		counts += ~X_isnan[X_argsort[:, i], i]

	# replace 0 counts with 1 to prevent numerical issues
	counts[counts == 0] = 1

	mean /= counts

	# apply mean values to data
	for i in range(X.shape[1]):
		X[X_argsort[:, i], i] = mean

	# recover nan values
	X[X_isnan] = np.nan



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

	if rank == 0:
		print("%d: loaded expression matrix: %s" % (rank, str(X.shape)))

	# load row names and column names
	BASENAME = ".".join(args.INPUT.split(".")[:-1])

	rownames = np.loadtxt("%s_rownames.txt" % BASENAME, dtype=str)
	colnames = np.loadtxt("%s_colnames.txt" % BASENAME, dtype=str)

	# perform log2 transform
	if args.LOG2:
		if rank == 0:
			print("Performing log2 transform...")

		transform_log2(X)

	# perform K-S test
	if args.KSTEST:
		if rank == 0:
			print("Performing K-S test and outlier removal...")

		mask = transform_kstest(X, colnames, keepna=args.KS_KEEPNA, threshold=args.KS_THRESHOLD, logfile=args.KS_LOG)

		# remove outliers from FPKM matrix
		if rank == 0:
			X = X[:, mask]
			colnames = colnames[mask]

	# perform quantile normalization
	if args.QUANTILE:
		if rank == 0:
			print("Performing quantile normalization...")

		transform_quantile(X)

	# save output matrix
	if rank == 0:
		print("Saving output expression matrix...")

		emx = pd.DataFrame(X, index=rownames, columns=colnames)
		emx.to_csv(args.OUTPUT, sep="\t", na_rep="NA", float_format="%.8f")
