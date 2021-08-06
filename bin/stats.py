#!/usr/bin/env python3
'''
Compute several summary statistics for an expression matrix.
'''
import argparse
import numpy as np
import pandas as pd
import sys

import utils



if __name__ == '__main__':
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('infile', help='input expression matrix (genes x samples)')

	args = parser.parse_args()

	# load input data
	emx = utils.load_dataframe(args.infile)
	emx = emx.values

	# print global stats
	print('shape: %s' % str(emx.shape))

	print('global:')
	print('  min:  %12.6f' % (np.nanmin(emx)))
	print('  mean: %12.6f' % (np.nanmean(emx)))
	print('  max:  %12.6f' % (np.nanmax(emx)))

	# print column-wise stats
	colmeans = np.nanmean(emx, axis=0)

	print('column-wise mean:')
	print('  min:  %12.6f' % (np.nanmin(colmeans)))
	print('  mean: %12.6f' % (np.nanmean(colmeans)))
	print('  max:  %12.6f' % (np.nanmax(colmeans)))
