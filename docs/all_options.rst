.. _all_options:

All parameters and options
================================

.. contents:: 
    :depth: 2

Parameter usage in general
---------------------------

You can specify all parameters and options of racoon either directly in the command line or in a config.yaml file provided with

.. code:: commandline

   racoon_clip run .. --configfile <your_configfile> --cores <n_cores>

To make your own config file you can start with an empty yaml file or copy one of the example config files `here <https://github.com/ZarnackGroup/racoon_clip/tree/main/minimal_examples>`_ and save it to a .yaml file. Then adjust the parameters as needed. All parameters, that should be used in default, do not need to be specified in the config.yaml file. Here is an example of a config.yaml file containing all default options:


.. code:: bash
    
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

In the command line every option can be specified by adding ``--`` in front and turning ``_`` to ""-"" in the option name. For example:

.. code:: commandline

   racoon_clip run ..  --configfile <your_configfile> --infiles <your_input_files> --barcodes-fasta <your_barcode_file.fasta>

.. note::

   If a parameter is specified in both the provided config file and the command line, the command line parameter will overwrite the config file.

racoon_clip will write a combined config file, containing the default options, where nothing was specified, the config file options and the command line options (command line parameters overwrite config file parameters) with the file ending "_updated.yaml" to keep track of the options you used.


Required input
---------------
The following input parameters are required from the user:

- infiles
- samples
- genome_fasta
- gtf
- either experiment_type or specific UMI and barcode length (umi1_len, umi2_len, encode_umi_length, exp_barcode_len, barcodeLength)
- read_length

See below for descriptions.

Input files and output directory
---------------------------------

- **wdir** (path): *default "./racoon_clip_out"*; Path where results are written to. A folder “results” containing all output will be created. Be aware that if a folder “results” already exists in this directory, it will be overwritten.

- **infiles** (path(s) to file(s)): One or multiple file paths to the fastq files of all samples. Multiple files should be provided in one string separated by a space. When demultiplexing should be performed by racoon_clip, specify only one input fastq file of the multiplexed reads. At the moment fasta files are not supported, as they will not allow any quality filtering.

- **seq_format** ("-Q33"/"-Q64"): *default "-Q33"*; Sequence format passed to FASTX-Toolkit. "-Q33" corresponds to data from an Illumina sequencer, "-Q64" would correspond to data from a Sanger sequencer.

Sample names & experiment groups
---------------------------------

- **samples** (string): A list of all sample names. The names should be the same as the file names of the input files or in case of demultiplexing should be the same as specified in the barcode file. Sample names are split by one space. Example: "sample_1 sample_2", when the corresponding input files are names sample_1.fastq, and sample_2.fastq. 
- **experiment_groups** (string): In addition to sample-wise output, racoon_clip will output merged bam and bw files. Which samples are merged together is specified by the experiment groups. Example: "WT KO". If all samples belong to the same group, this can be left empty and racoon_clip will automatically merge all samples. The groups must correspond to the group names specified in the experiment_group_file. 

- **experiment_group_file** (path to txt): *default " "*; A .txt file specifying which samples belong to which group. If all samples belong to the same condition, this can be left empty and racoon_clip will automatically merge all samples.

.. code-block:: text

   WT sample1
   WT sample2
   KO sample3
   KO sample4


Demultiplexing 
---------------------------------

Demultiplexing can optionally be performed. 

- **demultiplex** (True/False): *default False*; Whether demultiplexing still has to be done.
- **barcodes_fasta** (path to fasta): Path to fasta file of antisense sequences of used barcodes. Not needed if data is already demultiplexed. UMI sequences should be added as N. 

.. code-block:: text

   >min_expamle_iCLIP_s1
   NNNGGTTNN
   >min_expamle_iCLIP_s2
   NNNGGCGNN

Barcodes, UMIs and adapters
---------------------------------

Different experimental approaches (iCLIP, iCLIP2, eCLIP) will use different lengths and positions for barcodes, UMIs, and adaptors. The following schematic shows the most common barcode setups. 

- **iCLIP**: two UMI parts (3nt and 2nt) interspaced by the experimental barcode (4nt)

- **iCLIP2**: two UMI parts (5nt and 4nt) interspaced by the experimental barcode (6nt)

- **eCLIP:** UMI of 10nt (or 5nt) in the beginning (5' end) of read2 

- **eCLIP from ENCODE:** UMI of 10nt (or 5nt) in the beginning (5' end) of read2 is already trimmed off and stored in the read name

.. image:: ../experiment_types_schema.png
   :width: 600
    Most common barcode setups.


If your experiment used one of these setups, you can use the expereriment_type parameter:

Using a standard barcode setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **experiment_type** ("iCLIP"/"iCLIP2"/"eCLIP_5ntUMI"/"eCLIP_10ntUMI"/"eCLIP_ENCODE_5ntUMI"/"eCLIP_ENCODE_10ntUMI"/"noBarcode_noUMI"/"other"): *default: "other"*; The type of your experiment. 

.. Note::

   There is a special type eCLIP_ENCODE, because ENCODE provided data has the UMI information no longer in the read, but appended to the end of the read names.

Using manual barcode setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^
If your experiment does not follow one of these standard setups, you can define the setup manually and experiment_type defaults to other. In order to account for all of them and also allow other experimental setups racoon uses a barcode consisting of umi1+experimental_barcode+umi2 is used. Parts of this barcode that do not exist in a particular data set can be set to length 0. These are the parameters to manually set up your barcode+UMI architecture:

- **barcodeLength** (int): length of the complete barcode (UMI 1 + experimental barcode + UMI 2) 

- **umi1_len** (int): length of the UMI 1. Note that the sequences of the barcodes will be antisense of the barcodes used in the experiment. Therefore, UMI 1 is the 3' UMI of the experimental barcode. If the UMI is only 5' of the experimental barcode set to 0. 

-  **umi2_len** (int): length of the UMI 1. Note that the sequences of the barcodes will be antisense of the barcodes used in the experiment. Therefore, UMI 2 is the 5' UMI of the experimental barcode. If the UMI is only 3' of the experimental barcode set to 0. 

- **exp_barcode_len** (int): 0 if false exp_barcode_len should be 0, no barcode filtering will be done. 


For example, manually defining an iCLIP or eCLIP setup manually would look like this:

.. code-block:: python

   # iCLIP
   barcodeLength: 9
   umi1_len: 3
   umi2_len: 2
   exp_barcode_len: 4

   # eCLIP
   barcodeLength: 10 (5)
   umi1_len: 10 (5)
   umi2_len: 0
   exp_barcode_len: 0


Using manual barcode setup for ENCODE (or ENCODE-like) data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Note:: 

   This is needed for the older ENCODE eCLIP data where the UMI is only 5 nucleotides long

.. code-block:: python

   barcodeLength: 0 
   umi1_len: 5
   umi2_len: 0
   exp_barcode_len: 10
   encode: True   

Quality filtering during barcode trimming:
---------------------------------

- **flexbar_minReadLength** (int): *default 15*; The minimum length a read should have after trimming of barcodes, adapters and UMIs. Shorter reads are removed.

- **quality_filter_barcodes** (True/False): *default True*; Whether reads should be filtered for a minimum sequencing quality in the barcode sequence. 

- **minBaseQuality** (int): *default 10*; The minimum per base quality of the barcode region of each read. Reads below this threshold are filtered out. This only applies if quality_filter_barcodes is set to True. 

Adapters
-----------------
- **adapter_trimming** (True/False): *default True*; Whether adapter trimming should be performed. 

- **adapter_file** (path): *default /params.dir/adapters.fa*; A fasta file of adapters that should be trimmed. The default file contains the Illumina Universal adapter, the Illumina Multiplexing adapter and 20 eCLIP adapters. 

- **adapter_cycles** (int): *default 1*; How many cycles of adapter trimming should be performed. We recommend using 1 for iCLIP and iCLIP2 data and 2 for eCLIP.

Alignment to genome
---------------------------------

- **gft** (path): .gft file of used genome annotation. Note, that the file needs to be unzipped. (Can be obtained for example from https://www.gencodegenes.org/human/.) 

- **genome_fasta** : .fasta file of used genome annotation. Unzipped or bgzip files are supported. 

parameters  passed to STAR:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
(Check the `STAR manual <https://physiology.med.cornell.edu/faculty/skrabanek/lab/angsd/lecture_notes/STARmanual.pdf>`_ for a detailed description.) 

- **read_length** (int): *default 150*; The length of the new sequencing reads.

- **outFilterMismatchNoverReadLmax** (ratio): *default 0.04*; Ratio of allowed mismatches during alignment. Of outFilterMismatchNoverReadLmax and outFilterMismatchNmax the more stringent setting will be applied. 

- **outFilterMismatchNmax** (int): *default 999*; Number of allowed mismatches during alignment. Of outFilterMismatchNoverReadLmax and outFilterMismatchNmax the more stringent setting will be applied. 

- **outFilterMultimapNmax** (int): *default 1*; Maximum number of allowed multimappers. 

- **outSJfilterReads**: *default "Unique"*

- **moreSTARParameters**: Here all other STAR parameters can be passed.

Deduplication
--------------
- **deduplicate** (True/False): *default True*; Whether to perform deduplication. It is recommended to always use deduplication unless no UMIs are present in the data.


Execution parameters
--------------------
These parameters should be passed in the command line.

- ``--cores``: Number of cores for the execution.
- ``--verbose``: Print all commands of the process to the console.
- ``--log``: *default "racoon_clip.log"*; Name of log file.

Cluster execution
^^^^^^^^^^^^^^^^^^

- ``--profile``: The path to your cluster profile folder containing a config.yaml file that could for example look like this (For large datasets you might need to increase mem_mb and time.):

.. code-block:: bash
    
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
- ``--wait-for-files``: Should be specified when using a cluster execution.
- ``--latency-wait``: Should be specified when using a cluster execution. 60 is a possible value, depends on your workload manager.

See also:

    https://github.com/jdblischak/smk-simple-slurm/tree/main/examples/list-partitions
    https://snakemake.readthedocs.io/en/stable/executing/cluster.html






