# Unused FastQC rules
# These rules were removed from the main Snakefile because their outputs are not used in any reports
# They can be kept here for reference or re-enabled if needed in the future

# NOTE: If these rules are re-enabled, you will also need to add back to the main Snakefile:
# 1. The input list variables:
#    in_multiqc_bam = list()
#    in_multiqc_bam.append(expand("{wdir}/results/tmp/.fastqc.{sample}.bam.chkpnt", wdir=WDIR, sample=SAMPLES))
#
# 2. No myoutput entries were needed for the main pipeline BAM FastQC rules (they were not referenced in reports)
# 3. For miR FastQC rules, this myoutput entry was removed:
#    myoutput.append(expand("{wdir}/results/.fastqc.{sample}.trim.non_chimeric.chkpnt", wdir=WDIR, sample=SAMPLES))

###-----------------------------------------
### UNUSED BAM FastQC Rules (Main Pipeline)
###-----------------------------------------

# 3) after alignment
########################

rule fastqc_samples_bam:
    input:
        bam = get_bam_files
    output:
        touch("{wdir}/results/tmp/.fastqc.{sample}.bam.chkpnt")
    params: 
        wdir=config["wdir"],
        file=config["wdir"]+"/results/aligned/{sample}.Aligned.sortedByCoord.out.bam"
    conda:
        "envs/racoon_main_v0.4.yml"
    message: 
        "========================= \n FastQC of aligned {wildcards.sample} \n ================================ \n" 
    threads: 1
    shell:
        """
        mkdir -p {params.wdir}/results/fastqc/separate_samples_bam/ && \
        fastqc {input.bam} -o {params.wdir}/results/fastqc/separate_samples_bam/ -q
        """

rule multiqc_bam:
    input:
        in_multiqc_bam
    output:
        config["wdir"]+"/results/fastqc/separate_samples_bam/multiqc_report.html"
    params: wdir=config["wdir"]
    conda:
       "envs/racoon_main_v0.4.yml"
    message: 
        "========================= \n MultiQC of aligned \n ================================ \n" 
    threads: 1
    shell:
        """
          cd {params.wdir}/results/fastqc/separate_samples_bam/  && \
          multiqc -f --export .
          """


# 4) after dup removal
########################

rule fastqc_samples_bam_duprm:
    input:
        file=config["wdir"]+"/results/aligned/{sample}.Aligned.sortedByCoord.out.duprm.sort.bam"
    output:
        config["wdir"]+"/results/fastqc/separate_samples_bam_duprm/{sample}.Aligned.sortedByCoord.out.duprm.sort_fastqc.html"
    params: wdir=config["wdir"]
        # "results/fastqc/separate_samples/{sample}.html",
        # "results/fastqc/separate_samples/{sample}.zip"
    conda:
        "envs/racoon_main_v0.4.yml"
    message: 
        "========================= \n FastQC after duplicate removal {wildcards.sample} \n ================================ \n" 
    threads: 1
    shell:
        """
        mkdir -p {params.wdir}/results/fastqc/separate_samples_bam_duprm/ && \
        fastqc {input.file} -o {params.wdir}/results/fastqc/separate_samples_bam_duprm/ -q
        """

rule multiqc_bam_duprm:
    input:
        expand(config["wdir"]+"/results/fastqc/separate_samples_bam_duprm/{sample}.Aligned.sortedByCoord.out.duprm.sort_fastqc.html", sample=SAMPLES)
    output:
        config["wdir"]+"/results/fastqc/separate_samples_bam_duprm/multiqc_report.html"
    params: wdir=config["wdir"]
    conda:
       "envs/racoon_main_v0.4.yml"
    message: 
        "========================= \n MultiQC after duplicate removal \n ================================ \n" 
    threads: 1
    shell:
        """
        cd {params.wdir}/results/fastqc/separate_samples_bam_duprm/  && \
        multiqc -f --export .
        """


###-----------------------------------------
### UNUSED miR FastQC Rules
###-----------------------------------------

# 5) aligned miRs
####################
rule fastqc_aligned_mir:
    input:
        config["wdir"]+"/results/mir_analysis/aligned_mir/{sample}.alignMir.sam"
    output:
        config["wdir"]+"/results/mir_analysis/fastqc/aligend_mir/{sample}.alignMir_fastqc.html"
    params: wdir=config["wdir"]
    conda:
        "envs/racoon_main_v0.4.yml"
    threads: 1 # fastqc can use 1 thread per sample
    shell:
        """
        mkdir -p {params.wdir}/results/fastqc/aligned_mir && \
        fastqc {input} -o {params.wdir}/results/mir_analysis/fastqc/aligend_mir -q
        """


rule multiqc_aligned_mir:
    input:
        expand(config["wdir"]+"/results/mir_analysis/fastqc/aligend_mir/{sample}.alignMir_fastqc.html", sample = SAMPLES)
    output:
        config["wdir"]+"/results/mir_analysis/fastqc/aligend_mir/multiqc_report.html"
    params: wdir=config["wdir"]
    conda:
       "envs/racoon_main_v0.4.yml"
    threads: 1
    shell:
        """
        cd {params.wdir}/results/mir_analysis/fastqc/aligend_mir  && \
        multiqc -f --export .
        """

# 6) split trimmed chimeric reads
####################
rule fastqc_st_chimeric:
    input:
        config["wdir"]+"/results/mir_analysis/unaligned_target_RNAs/merged_fastq/{sample}.fastq.gz"
    output:
        config["wdir"]+"/results/mir_analysis/fastqc/split_chimeric/{sample}/multiqc_report.html"
    params:
        qc_dir=config["wdir"]+"/results/mir_analysis/fastqc/split_chimeric/{sample}",
        split_dir=config["wdir"]+"/results/mir_analysis/unaligned_target_RNAs/{sample}/"
    conda:
        "envs/racoon_main_v0.4.yml"
    threads: 1 # fastqc can use 1 thread per sample
    shell:
        """
        mkdir -p {params.qc_dir} && \
        chmod +x -R {params.qc_dir} && \
        fastqc {params.split_dir}*.fastq.gz -o {params.qc_dir} -q && \
        cd {params.qc_dir} && \
        ls && \
        multiqc -f --export .
        """


rule fastqc_samples_non_chimeric:
    input:
        file=get_demult_trim_reads
    output:
        touch("{wdir}/results/.fastqc.{sample}.trim.non_chimeric.chkpnt"),
    params: wdir=config["wdir"]
        # "results/fastqc/separate_samples/{sample}.html",
        # "results/fastqc/separate_samples/{sample}.zip"
    conda:
        "envs/racoon_main_v0.4.yml"
    threads: 1
    shell:
        """
        mkdir -p {params.wdir}/results/fastqc/non_chimeric/ && \
        fastqc {input.file} -o {params.wdir}/results/fastqc/non_chimeric/ -q
        """
