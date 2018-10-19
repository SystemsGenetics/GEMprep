import dataframe_helper
import numpy as np
import pandas as pd
import sys



if __name__ == "__main__":
	# parse command-line arguments
	if len(sys.argv) != 2:
		print("usage: python convert.py [infile]")
		sys.exit(-1)

	INFILE = sys.argv[1]

	# determine output format as opposite of input format
	basename, ext = dataframe_helper.split_filename(INFILE)

	if ext == "npy":
		OUTFILE = "%s.txt" % basename
	elif ext == "txt":
		OUTFILE = "%s.npy" % basename

	# load dataframe from input format
	print("Loading %s..." % INFILE)

	df = dataframe_helper.load(INFILE)

	# save dataframe in output format
	print("Saving %s..." % OUTFILE)

	dataframe_helper.save(OUTFILE, df)
