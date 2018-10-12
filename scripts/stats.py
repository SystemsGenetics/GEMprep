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

	# print stats
	print("min: %12.6f" % (emx.min().min()))
	print("avg: %12.6f" % (emx.sum().sum() / np.prod(emx.shape)))
	print("max: %12.6f" % (emx.max().max()))
