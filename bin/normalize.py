#!/usr/bin/env python3
'''
Perform any of a series of standard transformations to an
expression matrix, including log2 transform, outlier removal
via K-S test, and quantile normalization.

NOTE: The implementation of quantile normalization in this
script does not behave identically to normalize.quantiles()
in R when the input matrix has missing values.
'''
import argparse
import mpi4py.MPI as MPI
import numpy as np
import pandas as pd
import scipy.stats

import utils



# initialize MPI parameters
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()



def transform_log2(X, alpha=0):
	# transform each column
	for i in range(X.shape[1]):
		if rank == i % size:
			X_i = X[:, i]
			X_i[:] = np.log2(alpha + X_i)
			X_i[np.isinf(X_i)] = np.nan

	# gather columns
	for i in range(X.shape[1]):
		root = i % size
		comm.Bcast(X[:, i], root=root)



def transform_kstest(X, colnames, keepna=False, threshold=0.15, logfile=None):
	# extract global distribution
	g = X.reshape(-1, order='F')
	if not keepna:
		g = g[~np.isnan(g)]
	# g = scipy.stats.norm.cdf(g)

	print('%d: extracted global distribution: %s' % (rank, str(g.shape)))

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
		f = open(logfile, 'w')
		f.write('%s\t%s\t%s\n' % ('sample', 'd', 'p'))
		f.write('\n'.join([('%s\t%.6f\t%.6f' % (colname, d, p)) for (_, colname, d, p) in ks_results]))

	# return mask of non-outliers
	return [d < threshold for (_, _, d, p) in ks_results]



def transform_quantile(X, nanmean=False):
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
	mean = np.zeros(X.shape[0], dtype=X.dtype)

	for i in range(X.shape[1]):
		mean += X[X_argsort[:, i], i]

	if nanmean:
		# compute number of values in each row
		counts = np.zeros(X.shape[0], dtype=np.int32)

		for i in range(X.shape[1]):
			counts += ~X_isnan[X_argsort[:, i], i]

		# replace 0 counts with 1 to prevent numerical issues
		counts[counts == 0] = 1

		# compute mean by excluding nan values
		mean /= counts
	else:
		# compute mean by including nan values
		mean /= X.shape[1]

	# apply mean values to data
	for i in range(X.shape[1]):
		X[X_argsort[:, i], i] = mean

	# recover nan values
	X[X_isnan] = np.nan



if __name__ == '__main__':
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('infile', help='input expression matrix (genes x samples)')
	parser.add_argument('outfile', help='output expression matrix')
	parser.add_argument('--log2', help='perform a log2 transform', action='store_true')
	parser.add_argument('--log2-alpha', help='alpha value in log2 transform: x -> log2(alpha + x)', type=float, default=0)
	parser.add_argument('--kstest', help='perform outlier removal using the K-S test', action='store_true')
	parser.add_argument('--ks-log', help='log file of K-S test results')
	parser.add_argument('--ks-keepna', help='keep nan\'s during K-S test', action='store_true')
	parser.add_argument('--ks-threshold', help='threshold for K-S test', type=float, default=0.15)
	parser.add_argument('--quantile', help='perform quantile normalization', action='store_true')
	parser.add_argument('--quantile-nanmean', help='use nanmean during quantile normalization', action='store_true')

	args = parser.parse_args()

	# load input expression matrix
	if rank == 0:
		print('Loading input expression matrix...')

	emx = utils.load_dataframe(args.infile)

	# decompose dataframe into data, row names, and column names
	X = emx.values
	rownames = emx.index
	colnames = emx.columns

	# perform log2 transform
	if args.log2:
		if rank == 0:
			print('Performing log2 transform...')

		transform_log2(X, alpha=args.log2_alpha)

	# perform K-S test
	if args.kstest:
		if rank == 0:
			print('Performing outlier removal via K-S test...')

		mask = transform_kstest(X, colnames, keepna=args.ks_keepna, threshold=args.ks_threshold, logfile=args.ks_log)

		# remove outliers from FPKM matrix
		if rank == 0:
			print('Preserved %d / %d samples after outlier removal...' % (sum(mask), len(mask)))

			X = X[:, mask]
			colnames = colnames[mask]

	# perform quantile normalization
	if args.quantile:
		if rank == 0:
			print('Performing quantile normalization...')

		transform_quantile(X, nanmean=args.quantile_nanmean)

	# save output matrix
	if rank == 0:
		print('Saving output expression matrix...')

		emx = pd.DataFrame(X, index=rownames, columns=colnames)
		utils.save_dataframe(args.outfile, emx)
