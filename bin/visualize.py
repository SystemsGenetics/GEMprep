#!/usr/bin/env python3
'''
Create any of the following visualizations for an expression matrix:

- Density plot of expression values in each sample
- t-SNE plot of samples
'''
import matplotlib
matplotlib.use('Agg')

import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn.decomposition
import sklearn.manifold

import utils



def plot_density(
	X,
	filename,
	xmin=None,
	xmax=None):

	# compute x-axis limits if not provided
	if xmin == None:
		xmin = np.nanmin(X)

	if xmax == None:
		xmax = np.nanmax(X)

	# plot the KDE of each sample
	fig, ax = plt.subplots()

	for idx in X.index:
		X_i = X.loc[idx].dropna()
		sns.kdeplot(X_i, ax=ax)

	plt.title('Sample Distributions')
	plt.xlabel('Expression Level')
	plt.ylabel('Density')
	plt.xlim(xmin, xmax)

	if xmax - xmin < 100:
		plt.xticks(np.arange(int(xmin), int(xmax), 1))

	plt.savefig(filename)
	plt.close()



def broadcast(values, default=None, n_values=1):
	# apply default value
	if values == None:
		values = [default]

	# broadcast single value to list
	if len(values) == 1:
		values = [values[0] for _ in range(n_values)]

	return values



def plot_tsne(
	X, y,
	filename,
	na_value=np.nan,
	n_pca=None,
	classes=None,
	sizes=None,
	colors=None,
	alphas=None):

	# fill missing values with a representative value
	X = X.fillna(na_value)

	# perform PCA for dimensionality reduction
	print('  Computing PCA decomposition...')

	X_pca = sklearn.decomposition.PCA(n_components=n_pca, copy=False).fit_transform(X)

	# compute t-SNE from the PCA projection
	print('  Computing t-SNE...')

	X_tsne = sklearn.manifold.TSNE(n_components=2).fit_transform(X_pca)

	# plot the 2-D embedding
	plt.axis('off')

	# use discrete colors if y is categorical
	if y.dtype.kind in 'OSU':
		# use alphabetical order if not specified
		if classes == None:
			classes = list(set(y))

		# apply defaults to marker size, color, alpha
		sizes =  broadcast(sizes,  default=20,   n_values=len(classes))
		colors = broadcast(colors, default=None, n_values=len(classes))
		alphas = broadcast(alphas, default=1.0,  n_values=len(classes))

		# plot each class with its own display parameters
		for label, s, c, alpha in zip(classes, sizes, colors, alphas):
			plt.scatter(
				X_tsne[y == label, 0],
				X_tsne[y == label, 1],
				s=s, c=c, marker='o', alpha=alpha, edgecolors='w', label=label)

		# plot legend
		plt.subplots_adjust(right=0.70)
		plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

	# use colorbar if y is continuous
	else:
		# plot data
		plt.scatter(
			X_tsne[:, 0],
			X_tsne[:, 1],
			s=20, c=y, edgecolors='w')

		# plot colorbar
		plt.colorbar()

	# save figure to file
	plt.tight_layout()
	plt.savefig(filename)
	plt.close()



if __name__ == '__main__':
	# parse command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('infile', help='input expression matrix (samples x genes)')
	parser.add_argument('--labels', help='text file of sample labels')
	parser.add_argument('--density', help='save density plot to the given filename')
	parser.add_argument('--density-xmax', help='upper bound of x-axis', type=float)
	parser.add_argument('--tsne', help='save t-SNE plot to the given filename')
	parser.add_argument('--tsne-na', help='numerical value to use for missing values', type=float, default=-1e3)
	parser.add_argument('--tsne-npca', help='number of principal components to take before t-SNE', type=int)
	parser.add_argument('--tsne-classes', help='list of class labels for t-SNE plot (must match labels file)', nargs='+')
	parser.add_argument('--tsne-sizes', help='list of per-class marker sizes for t-SNE plot', type=int, nargs='+')
	parser.add_argument('--tsne-colors', help='list of per-class colors for t-SNE plot', nargs='+')
	parser.add_argument('--tsne-alphas', help='list of per-class alphas for t-SNE plot', type=float, nargs='+')

	args = parser.parse_args()

	# load input expression matrix
	emx = utils.load_dataframe(args.infile)

	print('Loaded %s %s' % (args.infile, str(emx.shape)))

	# load label file or generate empty labels
	if args.labels != None:
		labels = utils.load_labels(args.labels)
	else:
		labels = np.zeros(len(emx.index), dtype=str)

	print('Loaded %s %s' % ('labels', str(labels.shape)))

	# plot sample distributions
	if args.density != None:
		print('Plotting sample distributions...')

		plot_density(
			emx,
			args.density,
			xmax=args.density_xmax)

	# plot t-SNE of samples
	if args.tsne != None:
		print('Plotting 2-D t-SNE...')

		plot_tsne(
			emx,
			labels,
			args.tsne,
			na_value=args.tsne_na,
			n_pca=args.tsne_npca,
			classes=args.tsne_classes,
			sizes=args.tsne_sizes,
			colors=args.tsne_colors,
			alphas=args.tsne_alphas)
