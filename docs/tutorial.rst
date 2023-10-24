Tutorial
==========

.. contents:: 
    :depth: 2


Install racoon_clip as described :ref:`here <installation>`. 

Full list of yaml file options
------------------------------
Setting up racoon_clip works via providing a config.yaml file or by specifying all options in the command line. Here is a full config.yaml file including all default options. All parameters, that should be used in default, do not need to be specified in the config.yaml file. You can find an explanation of all parameters :ref:`here <all_options>`.

This tutorial will walk you through some minimal examples.

.. code:: python
    
    # where to put results
    wdir: "." # no backslash in the end of the path
    # input
    infiles: "" # one undemultiplexed file or multiple demultiplexed files
    
    #SAMPLES
    experiment_groups: "" # txt file with group space sample per row
    experiment_group_file: ""
    seq_format: "-Q33" # -Q33 for Illumnina -Q64 for Sanger needed by fastX
    
    # barcodes
    barcodeLength: "" # if already demux = umi1_len
    minBaseQuality: 10
    umi1_len: "" # antisense of used barcodes --> this is the 3' umi of the original barcode
    umi2_len: 0
    exp_barcode_len: 0
    encode: False
    
    experiment_type: "other" # one of "iCLIP", "iCLIP2", "eCLIP", "eCLIP_ENCODE" or "other" (if not "other this will overwrite "barcodeLength", "umi1_len", "umi2_len", "exp_barcode_len", "encode_umi")
    
    barcodes_fasta: "" # ! antisense of used barcodes, not needed if already demultiplexed
    quality_filter_barcodes: True # if no demultiplexing is done, should reads still be filtered for barcode / umi quality
    
    # demultiplexing
    demultiplex: False # Whether demultiplexing still has to be done, if FALSE exp_barcode_len should be 0, no bacode filtering will be done
    min_read_length: 15
    
    #adapter adapter_trimming
    adapter_file: ""
    adapter_cycles: 1
    adapter_trimming: True
    
    # star alignment
    gtf: "" # has to be unzipped at the moment
    genome_fasta: "" # has to be unzipped or bgzip
    read_length: 150 
    outFilterMismatchNoverReadLmax: 0.04
    outFilterMismatchNmax: 999
    outFilterMultimapNmax: 1
    outReadsUnmapped: "Fastx"
    outSJfilterReads: "Unique"
    moreSTARParameters: ""
    
    # deduplicate
    deduplicate: True

Get an annotation
------------------
First, download a human genome assembly (as fasta) and genome annotation (as gtf). You can for example get them from `GENCODE <https://www.gencodegenes.org/human/>`_ or from `ENSEMBL <http://www.ensembl.org/index.html>`_.

.. code:: bash

  mkdir annotation
  cd annotation
  wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/GRCh38.p14.genome.fa.gz
  wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gtf.gz
  gunzip *


Set up one of the minimal examples
-----------------------------------
Now you can run an example provided with racoon_clip.  Go into the folder minimal_examples and unzip the example, that you want to test. There are 4 examples, one for iCLIP, one for eCLIP, one for eCLIP downloaded from `ENCODE <https://www.encodeproject.org/>`_ and one for a multiplexed iCLIP (where racoon_clip needs to perform demultiplexing). In this tutorial, the iCLIP data set is shown exemplarily, but you can run this tutorial with each of these examples.

.. code:: bash

  cd minimal_examples
  unzip minimal_example_iCLIP.zip


Go into the folder of the example and unzip all files.

.. code:: bash

  cd minimal_examples/minimal_example_iCLIP
  gunzip *
  ls

You should now see the following files in the folder:

- **min_example_iCLIP_s1.fastq, min_example_iCLIP_s2.fastq**: Two samples with raw reads of an iCLIP experiment.

- **adapter.fa**: A fasta file containing the adapters used in the experiment. These will be trimmed off.

- **barcodes.fasta**: A fasta file containing the barcodes containing the experimental barcode and the UMI of each sample.
 
.. code:: bash

  head barcodes.fasta

  > >min_example_iCLIP_s1
  > NNNGGTTNN
  > >min_example_iCLIP_s2
  > NNNGGCGNN

- **groups.txt**:  A file specifying experiment groups. The group file has one line per sample. This line consists of first the group name and then the sample name. 

.. code:: bash

  head groups.txt
  
  > min_example_iCLIP min_example_iCLIP_s1
  > min_example_iCLIP min_example_iCLIP_s2

You can see that both samples belong to the group min_example_iCLIP. This example has only one group, the group.txt is not necessary. It is still shown here as an example. 

- **config_min_example_iCLIP.yaml**: The config file for racoon_clip. Inside the config file you need to adjust the path to the sample fastq files, the adapter.fa, the barcode.fasta, the group.txt and the annotation files, so they point to the right position on your machine.

.. Note::

  All paths need to be specified as absolute paths. Relative paths` (for example starting with ~) are not allowed.

Open the config file and change the paths with your favourite editor.

.. code:: python

    # where to put results
    wdir: "<path/to/output/dir>"
    
    # input
    infiles: "<path/to/minimal_example/minimal_example_iCLIP/min_example_iCLIP_s1.fastq>, "<path/to/minimal_example/minimal_example_iCLIP/min_example_iCLIP_s2.fastq>" # for multiple files after demultiplexing
    samples: "min_example_iCLIP_s1 min_example_iCLIP_s2"
    
    # barcodes
    experiment_type: "iCLIP"
    
    barcodes_fasta: ""<path/to/minimal_example/minimal_example_iCLIP/barcodes.fasta>" # ! antisense of used barcodes, not needed if already demultiplexed
    # make sure the barcodes have the same names as the samples
    
    # demultiplexing
    demultiplex: False # Whether demultiplexing still has to be done, if FALSE exp_barcode_len should be 0, no bacode filtering will be done
    
    #adapter adapter_trimming
    adapter_file: "<path/to/minimal_example/minimal_example_iCLIP/adapter.fa>"
    
    # star alignment
    gtf: "<path/to/annotation.gtf>" # has to be unzipped at the moment
    genome_fasta: "<path/to/genome.fa>" # has to be unzipped or bgzip
    read_length: 75 # readlength 

You should change the following lines:

.. code:: python

  wdir: "<path/where/to/put/results>"
  infiles: "<path/to/first/sample.fastq> <path/to/second/sample.fastq>"
  barcodes_fasta: "<path/to/barcodes.fasta>" # not needed for eCLIP data
  adapter_file: "<path/to/adapter/file>" 
  gtf: "<path/to/annotation.gtf>"
  genome_fasta: "<path/to/genome.fasta>"

.. Note::

  The eCLIP examples do not need the specification of a barcode_fasta and adapter_file. The barcodes in eCLIP are positioned at the read 1 (eCLIP is paired-end usually), but racoon only uses the read 2, which contains the crosslink site. For the adapters, the default adapters from racoon can be used for this example.

Selecting optional steps
------------------------

The following steps can be turned on and off as needed in the config file. (For the tutorial you can use the default options.)

+ **quality_filter_barcodes** (True/False): *default True*; Whether reads should be filtered for a minimum sequencing quality in the barcode sequence. The filter is applied on the combined region of UMI and barcode in iCLIP data or only UMI in eCLIP data and automatically turned off for experiment_type:"eCLIP_ENCODE".
+ **demultiplex** (True/False): *default False*; Whether demultiplexing still has to be done.
+ **adapter_trimming** (True/False): *default True*; Whether adapter trimming should be performed. 
+ **deduplicate** (True/False): *default True*; Whether to perform deduplication. It is recommended to always use deduplication unless no UMIs are present in the data.

Please also have a look at `options <all_options>` for how to provide barcode, UMI and adapter information.

.. code:: python
    quality_filter_barcodes:True/False
    demultiplex:False/True
    adapter_trimming:True/False
    deduplicate:deduplicate



Run the minimal example
------------------------

You can now run the minimal example:

.. code:: bash

  racoon_clip run --cores <n_cores> --configfile <path/to/config_min_example_iCLIP.yaml>

All resulting files will be written into a folder "results" inside your wdir.


Run the minimal example from the command line, without the config file
------------------------

You can also run racoon_clip without a config file. For the iCLIP example, you would need to provide the path information as described above and  specify the experiment_type "iCLIP" (which is already done in the example config file). 

.. code:: bash

  racoon_clip run --cores 6 \
  --experiment-type "iCLIP" \
  -wdir "<path/where/to/put/results>" \
  --infiles "<path/to/first/sample.fastq> <path/to/second/sample.fastq>" \
  --samples "min_example_iCLIP_s1 min_example_iCLIP_s2" \
  --barcodes-fasta "<path/to/barcodes.fasta>" \
  --adapter-file "<path/to/adapters.fasta>" \
  --gtf "<path/to/annotation.gtf>" \
  --genome-fasta "<path/to/genome.fasta>" \
  --read-length 75

For the other minimal examples, you would use "eCLIP" or "eCLIP_ENCODE" as experiment_type. 
 

.. code:: bash

  racoon_clip run --cores <n_cores> \
  --experiment_type "eCLIP" \
  -wdir "<path/where/to/put/results>" \
  --infiles "<path/to/first/sample.fastq> <path/to/second/sample.fastq>" \
  --gtf "<path/to/annotation.gtf>" \
  --genome_fasta "<path/to/genome.fasta>"
  --read-length 50


.. code:: bash

  racoon_clip run --cores <n_cores> \
  --experiment_type "eCLIP_ENCODE" \
  -wdir "<path/where/to/put/results>" \
  --infiles "<path/to/first/sample.fastq> <path/to/second/sample.fastq>" \
  --barcodes_fasta "<path/to/barcodes.fasta>" \
  --adapter_file "<path/to/adapter/file>" \
  --gtf "<path/to/annotation.gtf>" \
  --genome_fasta "<path/to/genome.fasta>"
  --read-length 45

For the multiplexed example you also need to specify ``--demultiplex True``. 
In addition, this example shows how to merge samples by groups with ``--experiment-groups`` and ``--experiment-group-file``.

.. code:: bash

  racoon_clip run --cores <n_cores> \
  --experiment_type "iCLIP2" \
  --demultiplex True \
  -wdir "<path/where/to/put/results>" \
  --infiles "<path/to/all_samples_multiplexed.fastq>"  \
  --barcodes_fasta "<path/to/barcodes.fasta>" \
  --adapter_file "<path/to/adapter/file>" \
  --gtf "<path/to/annotation.gtf>" \
  --genome_fasta "<path/to/genome.fasta>"
  --read-length 150 \
  --experiment-groups "min_example_iCLIP2_multiplexed_g1 min_example_iCLIP2_multiplexed_g2" \
  --experiment-group-file "<path/to/minimal_example_iCLIP_multiplexed/groups.txt>"


Understanding the output files
------------------------------
racoon_clip produces a variety of files during the different steps of the workflow. The files you will likely want to use downstream of racoon_clip are:

- **a summary of the performed steps** called Report.html.

- **The sample-wise whole aligned reads after duplicate removal in bam format**. You can find them in the folder results/aligned/<sample_name>.Aligned.sortedByCoord.out.duprm.bam together with the corresponding bam.bai files.

- **The group-wise whole aligned reads after duplicate removal in bam format.** There will be one bam file for each group you specified in the group.txt file. If no group is specified, you get a file called all.bam where all samples are merged. They are located in the results/bam_merged/ folder.

- **The sample-wise single nucleotide crosslink files in bw format.**: The files are split up into the plus and minus strands. They are located at results/bw/<sample_name>sortedByCoord.out.duprm.minus.bw and results/bw/<sample_name>sortedByCoord.out.duprm.plus.bw.

- **The group-wise single nucleotide crosslink files in bw format.**: The files are split up into the plus and minus strands. They are located at results/bw_merged/<sample_name>sortedByCoord.out.duprm.minus.bw and results/bw_merged/<sample_name>sortedByCoord.out.duprm.plus.bw.



Customising racoon_clip
---------------------------------------------------
racoon_clip offers many options to customise the workflow for your data. All settings can be passed to racoon_clip either in the command line or via a config file. For a full list of options please have a look at `options <all_options>` and

.. code:: bash

  racoon_clip run -h



Running racoon_clip with snakemakes cluster execution
--------------------------------------------

As racoon_clip is based on the snakemake workflow management system, in general, all snakemake commandline options can be passed to racoon_clip. For a full list of options check the :ref:`snakemake documentation <https://snakemake.readthedocs.io/en/stable/executing/cli.html>`. This applies also to the cluster execution and cloud execution of racoon_clip. 

For example, racoon_clip can be executed with slurm clusters like this:

.. code:: bash

  racoon_clip run \
  --configfile <your_configfile.yaml> \
  -p \
  --cores 10 \
  --profile <path/to/your/slurm/profile> \
  --wait-for-files \
  --latency-wait 60

Where <path/to/your/slurm/profile> should be a directory containing a config.yaml, that could for example look like this: 

.. code-block:: python

    cluster:
    mkdir -p logs/{rule} &&
    sbatch
    --cpus-per-task={threads}
    --mem={resources.mem_mb}
    --partition={resources.partition}
    --job-name=smk-{rule}-{wildcards}
    --output=logs/{rule}/{rule}-{wildcards}-%j.out
    default-resources:
    - partition=<your_partitions>
    - mem_mb=2000
    - time="48:00:00"
    jobs: 6


.. Note::

  For large datasets, you might need to increase mem_mb and time.


See also: 

+ https://github.com/jdblischak/smk-simple-slurm/tree/main/examples/list-partitions

+ https://snakemake.readthedocs.io/en/stable/executing/cluster.html





