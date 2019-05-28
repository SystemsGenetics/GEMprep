#!/usr/bin/env python

import argparse
import dataframe_helper
import pandas as pd
import random
import sys

if __name__ == "__main__":
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", required=True, help="input expression matrix", dest="INPUT")
	parser.add_argument("-p", "--partitions", help="partition label file", dest="PARTITIONS")
	parser.add_argument("-n", "--num-partitions", type=int, default=0, help="number of partitions to generate", dest="NUMPARTS")
	parser.add_argument("--method", default="uniform", choices=["random", "uniform"], help="partitioning method to use when generating partitions", dest="METHOD")
	parser.add_argument("--log", default="partitions.txt", help="log file of generated partition labels", dest="LOGFILE")

	args = parser.parse_args()

	# determine basename for output files
	basename, _ = dataframe_helper.split_filename(args.INPUT)

	# load input expression matrix
	print("Loading expression matrix...")

	emx = dataframe_helper.load(args.INPUT)

	# load or generate partition labels
	if args.PARTITIONS != None:
		print("Loading partition file...")

		pairs = pd.read_csv(args.PARTITIONS, header=None, names=["sample", "label"], sep="\t")
	elif args.NUMPARTS != 0:
		print("Generating partitions using the %s method..." % (args.METHOD))

		# generate labels
		labels = [str(i * args.NUMPARTS // emx.shape[1]) for i in range(emx.shape[1])]

		if args.METHOD == "random":
			random.shuffle(labels)
		elif args.METHOD == "uniform":
			pass

		# create pairs dataframe
		pairs = pd.DataFrame({ "sample": emx.columns, "label": labels })

		# save pairs to file
		print("Saving generated partition file...")

		pairs.to_csv(args.LOGFILE, sep="\t", header=False, index=False)
	else:
		print("error: you must specify either a partition file or partition generation method")
		sys.exit(-1)

	# save a sub-matrix for each partition
	partitions = list(set(pairs["label"]))
	partitions.sort()

	for p in partitions:
		# compute output name
		outname = "%s.%s.txt" % (basename, p)

		print("Saving %s..." % (outname))

		# extract partition sub-matrix
		samples = pairs.loc[pairs["label"] == p, "sample"]
		submatrix = emx[samples]

		# save submatrix
		dataframe_helper.save(outname, submatrix)
