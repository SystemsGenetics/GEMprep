import numpy as np
import pandas as pd
import sys



if __name__ == "__main__":
	# parse command-line arguments
	if len(sys.argv) != 2:
		print("usage: python text-to-bin.py [infile]")
		sys.exit(-1)

	INFILE = sys.argv[1]

	BASENAME = ".".join(INFILE.split(".")[:-1])
	OUTFILE_DATA = "%s.npy" % BASENAME
	OUTFILE_ROWNAMES = "%s_rownames.txt" % BASENAME
	OUTFILE_COLNAMES = "%s_colnames.txt" % BASENAME

	# load input matrix into dataframe
	df = pd.read_table(INFILE, index_col=0)

	print("Loaded %s %s" % (INFILE, str(df.shape)))

	# save data matrix to binary file
	np.save(OUTFILE_DATA, np.array(df.values, dtype=np.float32))

	# save row names and column names to text files
	np.savetxt(OUTFILE_ROWNAMES, df.index, fmt="%s")
	np.savetxt(OUTFILE_COLNAMES, df.columns, fmt="%s")

	print("Saved %s" % OUTFILE_DATA)
	print("Saved %s" % OUTFILE_ROWNAMES)
	print("Saved %s" % OUTFILE_COLNAMES)
