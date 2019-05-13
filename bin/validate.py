import argparse
import dataframe_helper
import numpy as np
import pandas as pd

if __name__ == "__main__":
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("--true", required=True, help="true expression matrix", dest="EMX_TRUE")
	parser.add_argument("--test", required=True, help="test expression matrix", dest="EMX_TEST")

	args = parser.parse_args()

	# load input dataframes
	emx_true = dataframe_helper.load(args.EMX_TRUE)
	emx_test = dataframe_helper.load(args.EMX_TEST)

	print("Loaded %s %s" % (args.EMX_TRUE, str(emx_true.shape)))
	print("Loaded %s %s" % (args.EMX_TEST, str(emx_test.shape)))

	# extract data matrix from each dataframe
	X_true = emx_true.values
	X_test = emx_test.values

	# print warnings for various mismatches
	if emx_true.shape != emx_test.shape:
		print("warning: shape does not match")

	if (emx_true.index != emx_test.index).any():
		print("warning: row names do not match")

	if (emx_true.columns != emx_test.columns).any():
		print("warning: column names do not match")

	# count the number of mismatched nans
	num_mismatched_nans = np.sum((np.isnan(X_true) != np.isnan(X_test)))

	print("number of mismatched nans: %d" % num_mismatched_nans)

	# compute difference
	diff = np.abs(X_true - X_test)

	# print stats
	print("min error: %12.6f" % (np.nanmin(diff)))
	print("avg error: %12.6f" % (np.nanmean(diff)))
	print("max error: %12.6f" % (np.nanmax(diff)))
