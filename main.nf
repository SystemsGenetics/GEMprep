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
		FPKM_FILES_FOR_CONVERT;
		FPKM_FILES_FOR_NORMALIZE;
		FPKM_FILES_FOR_VISUALIZE;
		FPKM_FILES_FOR_PARTITION
	}

GEM_FILES_FROM_INPUT
	.into {
		GEM_FILES_FOR_CONVERT;
		GEM_FILES_FOR_VISUALIZE;
		GEM_FILES_FOR_PARTITION
	}



/**
 * Gather expression matrix files for convert process.
 */
INPUT_FILES_FOR_CONVERT = FPKM_FILES_FOR_CONVERT.mix(GEM_FILES_FOR_CONVERT)



/**
 * The convert process takes an expression matrix and converts it from plaintext
 * to binary or vise versa.
 */
process convert {
	tag "${dataset}"
	publishDir "${params.output_dir}/${dataset}"

	input:
		set val(dataset), file(input_file) from INPUT_FILES_FOR_CONVERT

	output:
		set val(dataset), file("*.npy"), file("*_rownames.txt"), file("*_colnames.txt")

	when:
		params.convert.enabled == true

	script:
		"""
		convert.py ${input_file}
		"""
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
			--ks-log ${dataset}-ks-results.txt

		if [[ ${params.normalize.quantile} ]]; then
			mv ${dataset}_GEM.txt FPKM.txt
			normalize.R --quantile
			mv GEM.txt ${dataset}_GEM.txt
		fi
		"""
}



/**
 * Gather expression matrix files for visualize process.
 */
INPUT_FILES_FOR_VISUALIZE = FPKM_FILES_FOR_VISUALIZE.mix(GEM_FILES_FOR_VISUALIZE)



/**
 * The visualize process takes an expression matrix and produces a set of
 * visualizations based on the input configuration.
 */
process visualize {
	tag "${dataset}"
	publishDir "${params.output_dir}/${dataset}"

	input:
		set val(dataset), file(input_file) from INPUT_FILES_FOR_VISUALIZE

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



/**
 * Gather expression matrix files for partition process.
 */
INPUT_FILES_FOR_PARTITION = FPKM_FILES_FOR_PARTITION.mix(GEM_FILES_FOR_PARTITION)



/**
 * The partition process takes an expression matrix and produces several
 * sub-matrices based on a partitioning scheme.
 */
process partition {
	tag "${dataset}"
	publishDir "${params.output_dir}/${dataset}"

	input:
		set val(dataset), file(input_file) from INPUT_FILES_FOR_PARTITION

	output:
		set val(dataset), file("*.txt")

	when:
		params.partition.enabled == true

	script:
		"""
		partition.py \
			--input ${input_file} \
			--num-partitions ${params.partition.num_partitions} \
			--method ${params.partition.method} \
			--log partitions.txt
		"""
}
