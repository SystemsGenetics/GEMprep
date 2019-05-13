#!/usr/bin/env nextflow



/**
 * Create channel for input files.
 */
INPUT_FILES = Channel.fromFilePairs("${params.input_dir}/*_FPKM.txt", size: 1, flat: true)



process normalize {
	tag "${dataset}"
	publishDir "${params.output_dir}/${dataset}"

	input:
		set val(dataset), file(input_file) from INPUT_FILES

	output:
		set val(dataset), file("${dataset}_GEM.txt")

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
