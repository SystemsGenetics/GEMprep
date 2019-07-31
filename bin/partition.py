#!/usr/bin/env python3

import argparse
import pandas as pd
import random
import sys

import utils



if __name__ == "__main__":
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("infile", help="input expression matrix")
	parser.add_argument("outfile", help="output label file")
	parser.add_argument("--partitions", help="partition label file")
	parser.add_argument("--n-partitions", help="number of partitions to generate", type=int, default=0)
	parser.add_argument("--method", help="partitioning method to use when generating partitions", default="uniform", choices=["random", "uniform"])

	args = parser.parse_args()

	# determine basename for output files
	basename, _ = utils.split_filename(args.infile)

	# load input expression matrix
	print("Loading expression matrix...")

	emx = utils.load_dataframe(args.infile)

	# load partition labels from file
	if args.partitions != None:
		print("Loading partition file...")

		pairs = pd.read_csv(args.partitions, header=None, names=["sample", "label"], sep="\t")

	# or generate partitions
	elif args.n_partitions != 0:
		print("Generating partitions using the %s method..." % (args.method))

		# generate labels
		labels = [str(i * args.n_partitions // emx.shape[1]) for i in range(emx.shape[1])]

		if args.method == "random":
			random.shuffle(labels)
		elif args.method == "uniform":
			pass

		# create pairs dataframe
		pairs = pd.DataFrame({ "sample": emx.columns, "label": labels })

		# save pairs to file
		print("Saving generated partition file...")

		pairs.to_csv(args.outfile, sep="\t", header=False, index=False)

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
		utils.save_dataframe(outname, submatrix)
