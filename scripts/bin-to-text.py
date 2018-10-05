import numpy as np
import pandas as pd
import sys



if __name__ == "__main__":
	# parse command-line arguments
	if len(sys.argv) != 2:
		print("usage: python bin-to-text.py [infile]")
		sys.exit(-1)

	INFILE_DATA = sys.argv[1]

	BASENAME = ".".join(INFILE_DATA.split(".")[:-1])
	INFILE_ROWNAMES = "%s_rownames.txt" % BASENAME
	INFILE_COLNAMES = "%s_colnames.txt" % BASENAME
	OUTFILE = "%s.txt" % BASENAME

	# load data matrix, row names, and column names
	X = np.load(INFILE_DATA)
	rownames = np.loadtxt(INFILE_ROWNAMES, dtype=str)
	colnames = np.loadtxt(INFILE_COLNAMES, dtype=str)

	print("Loaded %s %s" % (INFILE_DATA, str(X.shape)))
	print("Loaded %s" % INFILE_ROWNAMES)
	print("Loaded %s" % INFILE_COLNAMES)

	# combine data, row names, and column names into dataframe
	df = pd.DataFrame(X, index=rownames, columns=colnames)

	# save dataframe
	df.to_csv(OUTFILE, sep="\t")

	print("Saved %s" % OUTFILE)
