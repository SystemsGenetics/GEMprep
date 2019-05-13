#!/usr/bin/env nextflow



/**
 * Create channel for input files.
 */
FPKM_FILES_FROM_INPUT = Channel.fromFilePairs("${params.input_dir}/*_FPKM.txt", size: 1, flat: true)
GEM_FILES_FROM_INPUT = Channel.fromFilePairs("${params.input_dir}/*_GEM.txt", size: 1, flat: true)



/**
 * Send input files to each process that uses them.
 */
FPKM_FILES_FROM_INPUT
	.into {
		FPKM_FILES_FOR_NORMALIZE;
		FPKM_FILES_FOR_VISUALIZE
	}



/**
 * The normalize process takes an FPKM expression matrix and applies a series
 * of transformations (log2, k-s test outlier removal, quantile normalization)
 * which produces a normalized expression matrix.
 */
process normalize {
	tag "${dataset}"
	publishDir "${params.output_dir}/${dataset}"

	input:
		set val(dataset), file(input_file) from FPKM_FILES_FOR_NORMALIZE

	output:
		set val(dataset), file("${dataset}_GEM.txt") into GEM_FILES_FROM_NORMALIZE

	when:
		params.normalize.enabled == true

	script:
		"""
		mpirun -np ${params.normalize.np} normalize.py \
			--input ${input_file} \
			--output ${dataset}_GEM.txt \
			${params.normalize.log2 ? "--log2" : ""} \
			${params.normalize.kstest ? "--kstest" : ""} \
			--ks-log ${dataset}-ks-results.txt \
			${params.normalize.quantile ? "--quantile" : ""} \
		"""
}



/**
 * Gather expression matrix files for visualize process.
 */
GEM_FILES_FOR_VISUALIZE = FPKM_FILES_FOR_VISUALIZE.mix(
	GEM_FILES_FROM_INPUT,
	GEM_FILES_FROM_NORMALIZE)



/**
 * The visualize process takes an expression matrix and produces a set of
 * visualizations based on the input configuration.
 */
process visualize {
	tag "${dataset}"
	publishDir "${params.output_dir}/${dataset}"

	input:
		set val(dataset), file(input_file) from GEM_FILES_FOR_VISUALIZE

	output:
		set val(dataset), file("*.png")

	when:
		params.visualize.enabled == true

	script:
		"""
		visualize.py \
			--input ${input_file} \
			${params.visualize.density ? "--density density.png" : ""}
		"""
}
