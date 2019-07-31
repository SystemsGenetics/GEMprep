#!/usr/bin/env nextflow



/**
 * Create channel for input files.
 */
FPKM_TXT_FILES_FROM_INPUT = Channel.fromFilePairs("${params.input.dir}/${params.input.fpkm_txt}", size: 1, flat: true)
RAW_TXT_FILES_FROM_INPUT = Channel.fromFilePairs("${params.input.dir}/${params.input.raw_txt}", size: 1, flat: true)
TPM_TXT_FILES_FROM_INPUT = Channel.fromFilePairs("${params.input.dir}/${params.input.tpm_txt}", size: 1, flat: true)
EMX_TXT_FILES_FROM_INPUT = Channel.fromFilePairs("${params.input.dir}/${params.input.emx_txt}", size: 1, flat: true)



/**
 * Send input files to each process that uses them.
 */
Channel.empty()
	.mix(
		FPKM_TXT_FILES_FROM_INPUT,
		RAW_TXT_FILES_FROM_INPUT,
		TPM_TXT_FILES_FROM_INPUT,
		EMX_TXT_FILES_FROM_INPUT
	)
	.into {
		DATA_TXT_FILES_FOR_CONVERT;
		DATA_TXT_FILES_FOR_NORMALIZE;
		DATA_TXT_FILES_FOR_VISUALIZE;
		DATA_TXT_FILES_FOR_PARTITION
	}



/**
 * The convert process takes an expression matrix and converts it from plaintext
 * to binary.
 */
process convert_txt_npy {
	tag "${dataset}"
	publishDir "${params.output.dir}/${dataset}"

	input:
		set val(dataset), file(input_file) from DATA_TXT_FILES_FOR_CONVERT

	output:
		set val(dataset), file("*.npy"), file("*.rownames.txt"), file("*.colnames.txt")

	when:
		params.convert_txt_npy.enabled == true

	script:
		"""
		convert.py ${input_file} \$(basename ${input_file} .txt).npy
		"""
}



/**
 * Make sure that at most one quantile method (R or python) is enabled.
 */
if ( params.normalize.quantile_py == true && params.normalize.quantile_r == true ) {
	error "error: only one quantile method (R or python) should be enabled"
}



/**
 * The normalize process takes an FPKM expression matrix and applies a series
 * of transformations (log2, k-s test outlier removal, quantile normalization)
 * which produces a normalized expression matrix.
 */
process normalize {
	tag "${dataset}"
	publishDir "${params.output.dir}/${dataset}"

	input:
		set val(dataset), file(input_file) from DATA_TXT_FILES_FOR_NORMALIZE

	output:
		set val(dataset), file("${dataset}.emx.txt")

	when:
		params.normalize.enabled == true

	script:
		"""
		mpirun --allow-run-as-root -np ${params.normalize.np} normalize.py \
			${input_file} \
			${dataset}.emx.txt \
			${params.normalize.log2 ? "--log2" : ""} \
			${params.normalize.kstest ? "--kstest" : ""} \
			--ks-log ${dataset}-ks-results.txt \
			${params.normalize.quantile_py ? "--quantile" : ""}

		if [[ ${params.normalize.quantile_r} == true ]]; then
			mv ${dataset}.emx.txt FPKM.txt
			normalize.R --quantile
			mv GEM.txt ${dataset}.emx.txt
		fi
		"""
}



/**
 * The visualize process takes an expression matrix and produces a set of
 * visualizations based on the input configuration.
 */
process visualize {
	tag "${dataset}"
	publishDir "${params.output.dir}/${dataset}"

	input:
		set val(dataset), file(input_file) from DATA_TXT_FILES_FOR_VISUALIZE

	output:
		set val(dataset), file("*.png")

	when:
		params.visualize.enabled == true

	script:
		"""
		visualize.py \
			${input_file} \
			${params.visualize.density ? "--density density.png" : ""} \
			${params.visualize.tsne ? "--tsne tsne.png" : ""} \
			--tsne-na ${params.visualize.tsne_na} \
			--tsne-npca ${params.visualize.tsne_npca}
		"""
}



/**
 * The partition process takes an expression matrix and produces several
 * sub-matrices based on a partitioning scheme.
 */
process partition {
	tag "${dataset}"
	publishDir "${params.output.dir}/${dataset}"

	input:
		set val(dataset), file(input_file) from DATA_TXT_FILES_FOR_PARTITION

	output:
		set val(dataset), file("*.txt")

	when:
		params.partition.enabled == true

	script:
		"""
		partition.py \
			${input_file} \
			partitions.txt \
			--n-partitions ${params.partition.num_partitions} \
			--method ${params.partition.method}
		"""
}
