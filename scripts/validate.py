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
	df_true = pd.read_table(args.EMX_TRUE, index_col=0)
	df_test = pd.read_table(args.EMX_TEST, index_col=0)

	# compute difference
	diff = abs(df_true - df_test)

	# print stats
	print("min error: %12.6f" % (diff.min().min()))
	print("avg error: %12.6f" % (diff.sum().sum() / np.prod(diff.shape)))
	print("max error: %12.6f" % (diff.max().max()))
