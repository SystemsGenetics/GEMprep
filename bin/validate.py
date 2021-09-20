#!/usr/bin/env python3
'''
Compare various summary statistics of two expression matrices. Useful
for verifying that two GEMs are identical or for quantifying the
differences between them.
'''
import argparse
import numpy as np
import pandas as pd

import utils



if __name__ == '__main__':
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('emx_true', help='true expression matrix')
	parser.add_argument('emx_test', help='test expression matrix')

	args = parser.parse_args()

	# load input dataframes
	emx_true = utils.load_dataframe(args.emx_true)
	emx_test = utils.load_dataframe(args.emx_test)

	print('Loaded %s %s' % (args.emx_true, str(emx_true.shape)))
	print('Loaded %s %s' % (args.emx_test, str(emx_test.shape)))

	# extract data matrix from each dataframe
	X_true = emx_true.to_numpy()
	X_test = emx_test.to_numpy()

	# print warnings for various mismatches
	if emx_true.shape != emx_test.shape:
		print('warning: shape does not match')

	if (emx_true.index != emx_test.index).any():
		print('warning: row names do not match')

	if (emx_true.columns != emx_test.columns).any():
		print('warning: column names do not match')

	# count the number of mismatched nans
	num_mismatched_nans = np.sum((np.isnan(X_true) != np.isnan(X_test)))

	print('number of mismatched nans: %d' % num_mismatched_nans)

	# compute difference
	diff = np.abs(X_true - X_test)

	# count the number of errors
	num_errors = np.sum(diff > 1e-6)

	print('number of errors: %d' % num_errors)

	# print stats
	print('min error: %12.6f' % (np.nanmin(diff)))
	print('avg error: %12.6f +/- %12.6f' % (np.nanmean(diff), np.nanstd(diff)))
	print('max error: %12.6f' % (np.nanmax(diff)))
