#!/usr/bin/env python

import numpy as np
import pandas as pd
import sys

import utils



if __name__ == "__main__":
	# parse command-line arguments
	if len(sys.argv) != 2:
		print("usage: python convert.py [infile]")
		sys.exit(-1)

	INFILE = sys.argv[1]

	# determine output format as opposite of input format
	basename, ext = utils.split_filename(INFILE)

	if ext == "npy":
		OUTFILE = "%s.txt" % basename
	elif ext == "txt":
		OUTFILE = "%s.npy" % basename

	# load dataframe from input format
	print("Loading %s..." % INFILE)

	df = utils.load_dataframe(INFILE)

	# save dataframe in output format
	print("Saving %s..." % OUTFILE)

	utils.save_dataframe(OUTFILE, df)
