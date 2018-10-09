import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

if __name__ == "__main__":
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", required=True, help="input expression matrix", dest="INPUT")
	parser.add_argument("-o", "--output", default="dist.png", help="output plot file", dest="PLOTFILE")

	args = parser.parse_args()

	# load input data
	emx = pd.read_table(args.INPUT, index_col=0)

	# plot sample distributions
	_, ax = plt.subplots(figsize=(10, 10))

	for colname in emx.columns:
		x = emx[colname].dropna()
		sns.distplot(x, hist=False, ax=ax)

	plt.title("Sample Distributions: %s" % (args.INPUT))
	plt.xlim(emx.min().min(), emx.max().max())
	plt.xlabel("Expression Level")
	plt.ylabel("Density")
	plt.savefig(args.PLOTFILE)
