#!/home/reimen/bin nextflow

process pbs {

        publishDir '/scratch2/reimen/nextflowTests/pbs/direct/gemPrepDirect'

        executor "pbs"

        tag { normalize }

        conda "/home/reimen/.conda/envs/myenv"

        module 'purge'
        module 'anaconda3/5.1.0'
        module 'gcc/7.1.0 openmpi/1.8.4 pgi/2016'

        """
                INFILE=$params.pbs.input.inputGEM
                OUTFILE=$params.pbs.output.outputGEM
              	LOGFILE=$params.pbs.output.outputKS

                        cd /scratch2/reimen/nextflowTests/pbs/direct/gemPrepDirect

                
                python $params.pbs.input.normalizeScript \
                        --input \$INFILE \
                        --output \$OUTFILE \
                        --log2 \
                        --kstest \
                        --ks-log \$LOGFILE \
                        --quantile
        """

}

