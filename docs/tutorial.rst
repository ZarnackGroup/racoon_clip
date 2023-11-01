Tutorial
================================

.. contents:: 
    :depth: 2


How to run racoon_clip
---------------------------

You can run racoon_clip with the following command:

.. code:: commandline

   racoon_clip run --configfile <your_configfile> --cores <n_cores> [OPTIONS]

Execution parameters
^^^^^^^^^^^^^^^^^^^^
These parameters should be passed in the command line.

- ``--cores``: Number of cores for the execution.
- ``--verbose``: Print all commands of the process to the console.
- ``--log``: *default "racoon_clip.log"*; Name of log file.

How to pass workflow parameters to racoon_clip
---------------------------

You can specify all workflow parameters and options of racoon_clip either directly in the command line or in a config file config.yaml file.

Here is a config file listing all default options. This tutorial will walk you through most parameters, you can find a complete explanation of all parameters :ref:`here <all_options>`.

.. code:: python
    
    # Where to put results
    wdir: "." # No backslash in the end of the path
    # input
    infiles: "" # one un-demultiplexed file or multiple demultiplexed files
    
    #SAMPLES
    experiment_groups: "" # txt file with group space sample per row
    experiment_group_file: ""
    seq_format: "-Q33" # -Q33 for Illumina -Q64 for Sanger needed by fastX
    
    # barcodes
    barcodeLength: "" # if already demux = umi1_len
    minBaseQuality: 10
    umi1_len: "" # antisense of used barcodes --> this is the 3' umi of the original barcode
    umi2_len: 0
    exp_barcode_len: 0
    encode: False
    
    experiment_type: "other" # one of "iCLIP", "iCLIP2", "eCLIP_5ntUMI", "eCLIP_10ntUMI", "eCLIP_ENCODE_5ntUMI", "eCLIP_ENCODE_10ntUMI", "noBarcode_noUMI" or "other" (if not "other this will overwrite "barcodeLength", "umi1_len", "umi2_len", "exp_barcode_len", "encode_umi")
    
    barcodes_fasta: "" # ! antisense of used barcodes, not needed if already demultiplexed
    quality_filter_barcodes: True # if no demultiplexing is done, should reads still be filtered for barcode / umi quality
    
    # demultiplexing
    demultiplex: False # Whether demultiplexing still has to be done, if FALSE exp_barcode_len should be 0, no barcode filtering will be done
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

All these options can also be specified in the command line instead of the config file. For the command line parameters check out

.. code:: bash

   racoon_clip run -h


What you need to specify 
---------------------------

The following input is required from the user:

- infiles
- samples
- genome_fasta
- gtf
- either experiment_type or specific UMI and barcode length (umi1_len, umi2_len, encode_umi_length, exp_barcode_len, barcodeLength)
- read_length
- in some cases a barcode fasta (for the demultiplexing functionality or for data with an iCLIP or iCLIP2 barcode included)

A minimal config file would therefore look like this

.. code:: python
    
    # where to put results
    wdir: "output/path" # no backslash in the end of the path
    # input
    infiles: "path/to/sample1.fastq path/to/sample2.fastq" # one un-demultiplexed file or multiple demultiplexed files
    samples: "sample1 sample2"
    # annotation
    gtf: "path/to/annotation.gtf" # has to be unzipped at the moment
    genome_fasta: "path/to/genome_assembly.fa" # has to be unzipped or bgzip
    read_length: N 

    # experiemnt type
    experiment_type: "iCLIP"/"iCLIP2"/"eCLIP_5ntUMI"/"eCLIP_10ntUMI"/"eCLIP_ENCODE_5ntUMI"/"eCLIP_ENCODE_10ntUMI"/"noBarcode_noUMI"/"other" 

    # for the demultiplexing functionality or for data with experiment_type "iCLIP" or "iCLIP2"
    barcodes_fasta: "path/to/barcodes.fasta" # barcodes need to have the same names as specified in the samples parameter above

Which steps will racoon_clip run by default
---------------------------
This depends on the experiment_type. If not specified otherwise racoon_clip will run the following:

| **iCLIP, iCLIP2 and other:** 
| Quality Control > Barcode and Adapter trimming > Alignment > Deduplication > Crosslink detection
|
| **eCLIP_5ntUMI and eCLIP_10ntUMI:** 
| Quality Control > UMI and Adapter trimming > Alignment > Deduplication > Crosslink detection
|
| **eCLIP_ENCODE_5ntUMI and eCLIP_ENCODE_10ntUMI:** 
| Adapter trimming > Alignment > Deduplication > Crosslink detection
|
| **noBarcode_noUMI:**
| Adapter trimming > Alignment > Crosslink detection

How to turn optional steps on or off
--------------------------------------
You can use the following parameters to turn steps on or off:

.. code:: python

    demultiplex: True/False
    quality_filter_barcodes: True/False
    adapter_trimming: True/False
    deduplicate: True/False


Demultiplexing 
^^^^^^^^^^^^^^^^^
Demultiplexing is at the moment only possible for single-end read data. Both the UMI and the barcode need to be positioned in the beginning of the read.

- **demultiplex** (True/False): *default False*; Whether demultiplexing still has to be done.
- **barcodes_fasta** (path to fasta): Path to fasta file of antisense sequences of used barcodes. Not needed if data is already demultiplexed. UMI sequences should be added as N. 

This is an example of a barcode fasta for an iCLIP experiment. It is important that the barcode names (after >) are exactly the same as the specified sample names and the names of the input read files. The UMIs are added as Ns.

.. code-block:: text

   >min_expamle_iCLIP_s1
   NNNGGTTNN
   >min_expamle_iCLIP_s2
   NNNGGCGNN

Quality filtering during barcode trimming
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **flexbar_minReadLength** (int): *default 15*; The minimum length a read should have after trimming of barcodes, adapters and UMIs. Shorter reads are removed.

- **quality_filter_barcodes** (True/False): *default True*; Whether reads should be filtered for a minimum sequencing quality in the barcode sequence. 

- **minBaseQuality** (int): *default 10*; The minimum per base quality of the barcode region of each read. Reads below this threshold are filtered out. This only applies if quality_filter_barcodes is set to True. 

Adapters
^^^^^^^^^^
- **adapter_trimming** (True/False): *default True*; Whether adapter trimming should be performed. 

- **adapter_file** (path): *default /params.dir/adapters.fa*; A fasta file of adapters that should be trimmed. The default file contains the Illumina Universal adapter, the Illumina Multiplexing adapter and 20 eCLIP adapters. 

- **adapter_cycles** (int): *default 1*; How many cycles of adapter trimming should be performed. We recommend using 1 for iCLIP and iCLIP2 data and 2 for eCLIP.


Deduplication
^^^^^^^^^^^^^^
- **deduplicate** (True/False): *default True*; Whether to perform deduplication. It is recommended to always use deduplication unless no UMIs are present in the data.



Preset and custom options Barcodes and UMIs 
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

- **experiment_type** ("iCLIP"/"iCLIP2"/"eCLIP_5ntUMI"/"eCLIP_10ntUMI"/"eCLIP_ENCODE_5ntUMI"/"eCLIP_ENCODE_10ntUMI"/"noBarcode_noUMI"/"other"): *default: "other"*; The type of your barcode setup. 

.. Note::

   There is a special type eCLIP_ENCODE, because ENCODE provided data has the UMI information no longer in the read, but appended to the end of the read names.

Using manual barcode setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^
If your data does not follow one of these standard setups, you can define the setup manually and experiment_type defaults to other. In order to account for all of them and also allow other experimental setups racoon uses a barcode consisting of **umi1 + experimental_barcode + umi2** is used. Parts of this barcode that do not exist in a particular data set can be set to length 0. These are the parameters to manually set up your barcode&UMI architecture:

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


How to customise genome alignment
---------------------------------

Required input
^^^^^^^^^^^^^^^
- **gtf** (path): .gft file of used genome annotation. Note, that the file needs to be unzipped. (Can be obtained for example from https://www.gencodegenes.org/human/.) 

- **genome_fasta** : .fasta file of used genome annotation. Unzipped or bgzip files are supported. 

- **read_length** (int): *default 150*; The length of the new sequencing reads.

You can, for example, get the gtf and the genome_fasta from `GENCODE <https://www.gencodegenes.org/human/>`_ or from `ENSEMBL <http://www.ensembl.org/index.html>`_.

.. code:: bash

  mkdir annotation
  cd annotation
  wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/GRCh38.p14.genome.fa.gz
  wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gtf.gz
  gunzip *

Additional parameters 
^^^^^^^^^^^^^^^^^^^^^
Multiple additional parameters can be passed for the alignment. For example, multimapping reads can be allowed with:

- **outFilterMultimapNmax** (int): *default 1*; Maximum number of allowed multimappers. 

Furthermore, these parameters can fine-tune the stringency of the alignment:

- **outFilterMismatchNoverReadLmax** (ratio): *default 0.04*; Ratio of allowed mismatches during alignment. Of outFilterMismatchNoverReadLmax and outFilterMismatchNmax the more stringent setting will be applied. 

- **outFilterMismatchNmax** (int): *default 999*; Number of allowed mismatches during alignment. Of outFilterMismatchNoverReadLmax and outFilterMismatchNmax the more stringent setting will be applied. 

- **outSJfilterReads**: *default "Unique"*

There is also an option to pass all other STAR parameters with:

- **moreSTARParameters**: Here all other STAR parameters can be passed.

Check the `STAR manual <https://physiology.med.cornell.edu/faculty/skrabanek/lab/angsd/lecture_notes/STARmanual.pdf>`_ for a detailed description and all options.


How to run racoon_clip with snakemakes cluster execution
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

    

