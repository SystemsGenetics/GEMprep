import numpy as np
import pandas as pd
import sys

import utils



if __name__ == "__main__":
	# parse command-line arguments
	if len(sys.argv) != 2:
		print("usage: python stats.py [infile]")
		sys.exit(-1)

	INFILE = sys.argv[1]

	# load input data
	emx = utils.load_dataframe(INFILE)
	emx = emx.values

	# print global stats
	print("shape: %s" % str(emx.shape))

	print("global:")
	print("  min: %12.6f" % (np.nanmin(emx)))
	print("  avg: %12.6f" % (np.nanmean(emx)))
	print("  max: %12.6f" % (np.nanmax(emx)))

	# print column-wise stats
	colmeans = np.nanmean(emx, axis=0)

	print("column-wise mean:")
	print("  min: %12.6f" % (np.nanmin(colmeans)))
	print("  avg: %12.6f" % (np.nanmean(colmeans)))
	print("  max: %12.6f" % (np.nanmax(colmeans)))
