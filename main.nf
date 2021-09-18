#!/usr/bin/env nextflow

nextflow.enable.dsl=2



workflow {
    // load input files
    fpkm_txt_files = Channel.fromFilePairs("${params.input_dir}/${params.fpkm_txt}", size: 1, flat: true)
    raw_txt_files  = Channel.fromFilePairs("${params.input_dir}/${params.raw_txt}", size: 1, flat: true)
    tpm_txt_files  = Channel.fromFilePairs("${params.input_dir}/${params.tpm_txt}", size: 1, flat: true)
    emx_txt_files  = Channel.fromFilePairs("${params.input_dir}/${params.emx_txt}", size: 1, flat: true)
    labels_files   = Channel.fromFilePairs("${params.input_dir}/${params.labels_txt}", size: 1, flat: true)

    data_txt_files = Channel.empty().mix(
        fpkm_txt_files,
        raw_txt_files,
        tpm_txt_files,
        emx_txt_files
    )

    // run convert if specified
    if ( params.convert_txt_npy == true ) {
        convert_txt_npy(data_txt_files)
    }

    // make sure that at most one quantile method (R or python) is enabled
    if ( params.normalize_quantile_py == true && params.normalize_quantile_r == true ) {
        error "error: only one quantile method (R or python) should be enabled"
    }

    // run normalize if specified
    if ( params.normalize == true ) {
        normalize(data_txt_files)
    }

    // run visualize if specified
    if ( params.visualize == true ) {
        visualize(data_txt_files, labels_files)
    }

    // run partition if specified
    if ( params.partition == true ) {
        partition(data_txt_files)
    }
}



/**
 * The convert process takes an expression matrix and converts it from plaintext
 * to binary.
 */
process convert_txt_npy {
    tag "${dataset}"
    publishDir "${params.output_dir}/${dataset}"

    input:
        tuple val(dataset), path(input_file)

    output:
        tuple val(dataset), path("*.npy"), path("*.rownames.txt"), path("*.colnames.txt")

    script:
        """
        convert.py ${input_file} `basename ${input_file} .txt`.npy
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
        tuple val(dataset), path(input_file)

    output:
        tuple val(dataset), path("${dataset}.emx.txt")
        tuple val(dataset), path("${dataset}.kstest.txt")

    script:
        """
        mpirun -np ${params.normalize_np} normalize.py \
            ${input_file} \
            ${dataset}.emx.txt \
            ${params.normalize_log2 ? "--log2" : ""} \
            ${params.normalize_kstest ? "--kstest" : ""} \
            --ks-log ${dataset}.kstest.txt \
            ${params.normalize_quantile_py ? "--quantile" : ""}

        if [[ ${params.normalize_quantile_r} == true ]]; then
            mv ${dataset}.emx.txt FPKM.txt
            normalize_R --quantile
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
    publishDir "${params.output_dir}/${dataset}"

    input:
        tuple val(dataset), path(data_file)
        tuple val(dataset), path(labels_file)

    output:
        tuple val(dataset), path("*.png")

    script:
        """
        visualize.py \
            ${data_file} \
            --labels ${labels_file} \
            ${params.visualize_density ? "--density density.png" : ""} \
            ${params.visualize_tsne ? "--tsne tsne.png" : ""} \
            --tsne-na ${params.visualize_tsne_na} \
            --tsne-npca ${params.visualize_tsne_npca}
        """
}



/**
 * The partition process takes an expression matrix and produces several
 * sub-matrices based on a partitioning scheme.
 */
process partition {
    tag "${dataset}"
    publishDir "${params.output_dir}/${dataset}"

    input:
        tuple val(dataset), path(input_file)

    output:
        tuple val(dataset), path("*.txt")

    script:
        """
        partition.py \
            ${input_file} \
            partitions.txt \
            --n-partitions ${params.partition_npartitions} \
            --method ${params.partition_method}
        """
}
