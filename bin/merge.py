#!/usr/bin/env python3
'''
Merge several expression matrices into one matrix.
'''
import argparse
import pandas as pd

import utils



if __name__ == '__main__':
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('infiles', help='Input dataframes', nargs='*')
	parser.add_argument('outfile', help='Output dataframe')

	args = parser.parse_args()

	# initialize output expression matrix and labels
	X = pd.DataFrame()
	y = pd.DataFrame()

	# load each input file into expression matrix
	for infile in args.infiles:
		# load input file
		print('loading \'%s\'' % infile)

		X_i = pd.read_csv(infile, sep='\t', index_col=0)

		# remove extraneous columns
		X_i.drop(columns=['Entrez_Gene_Id'], inplace=True)

		# extract labels
		label = infile.split('.')[0].split('/')[-1]
		y_i = pd.DataFrame({'sample': X_i.columns, 'label': label})

		# append input dataframe to output dataframe
		X = pd.merge(X, X_i, left_index=True, right_index=True, how='outer')

		# append input labels to ouput labels
		y = y.append(y_i)

	y.set_index('sample', inplace=True)

	# save output expression matrix
	print('saving \'%s\'' % args.outfile)

	utils.save_dataframe(args.outfile, X)
	utils.save_dataframe('%s.labels.txt' % args.outfile.split('.')[0], y)
