import argparse
import numpy as np
import pandas as pd

import utils



if __name__ == "__main__":
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("emx_true", help="true expression matrix")
	parser.add_argument("emx_test", help="test expression matrix")

	args = parser.parse_args()

	# load input dataframes
	emx_true = utils.load_dataframe(args.emx_true)
	emx_test = utils.load_dataframe(args.emx_test)

	print("Loaded %s %s" % (args.emx_true, str(emx_true.shape)))
	print("Loaded %s %s" % (args.emx_test, str(emx_test.shape)))

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
