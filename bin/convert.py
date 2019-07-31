#!/usr/bin/env python3

import argparse
import numpy as np
import pandas as pd
import sys

import utils



if __name__ == "__main__":
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("infile", help="input expression matrix")
	parser.add_argument("outfile", help="output expression matrix")
	parser.add_argument("--transpose", help="Transpose the input file", action="store_true")

	args = parser.parse_args()

	# load input dataframe from input format
	print("Loading %s..." % args.infile)

	df = utils.load_dataframe(args.infile)

	# transpose dataframe if specified
	if args.transpose:
		print("transposing matrix...")
		df = df.T

	# save dataframe in output format
	print("Saving %s..." % args.outfile)

	utils.save_dataframe(args.outfile, df)
