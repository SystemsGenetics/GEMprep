import argparse
import numpy as np
import pandas as pd

if __name__ == "__main__":
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("--true", required=True, help="true expression matrix", dest="EMX_TRUE")
	parser.add_argument("--test", required=True, help="test expression matrix", dest="EMX_TEST")

	args = parser.parse_args()

	# load input dataframes
	X_true = pd.read_table(args.EMX_TRUE, index_col=0)
	X_test = pd.read_table(args.EMX_TEST, index_col=0)

	print("Loaded %s %s" % (args.EMX_TRUE, str(X_true.shape)))
	print("Loaded %s %s" % (args.EMX_TEST, str(X_test.shape)))

	# separate dataframes into data, row names, and column names
	X_true_rownames = X_true.index
	X_true_colnames = X_true.columns
	X_true = X_true.values

	X_test_rownames = X_test.index
	X_test_colnames = X_test.columns
	X_test = X_test.values

	# print warnings for various mismatches
	if X_true.shape != X_test.shape:
		print("warning: shape does not match")

	if (X_true_rownames != X_test_rownames).any():
		print("warning: row names do not match")

	if (X_true_colnames != X_test_colnames).any():
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
