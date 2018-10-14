import numpy as np
import pandas as pd
import sys

if __name__ == "__main__":
	# parse command-line arguments
	if len(sys.argv) != 2:
		print("usage: python stats.py [infile]")
		sys.exit(-1)

	INFILE = sys.argv[1]

	# load input data
	emx = pd.read_table(INFILE, index_col=0)
	emx = emx.values

	# print stats
	print("min: %12.6f" % (np.nanmin(emx)))
	print("avg: %12.6f" % (np.nanmean(emx)))
	print("max: %12.6f" % (np.nanmax(emx)))

	# compute column means
	colmeans = np.nanmean(emx, axis=0)

	print("column mean: %.6f +/- %.6f" % (colmeans.mean(), colmeans.std()))
