.. _all_options:

All parameters and options
================================

.. contents:: 
    :depth: 2

Parameter usage in general
---------------------------

You can specify workflow parameters in a configuration file or through the
corresponding command-line option. Configuration keys retain their exact
spelling, including underscores and capitalization. Command-line spellings
must match the options shown by the help command and are not produced by one
universal underscore-to-hyphen rule.

.. code:: bash

   racoon_clip crosslinks --configfile <your_configfile> --cores <n_cores>
   racoon_clip peaks --configfile <your_configfile> --cores <n_cores>

To make your own config file, you can start with an empty YAML file or copy
one of the files in
`example_data <https://github.com/ZarnackGroup/racoon_clip/tree/main/example_data>`_.
Then adjust the parameters as needed. Parameters that use their defaults do
not need to be specified. The existing default example below is retained
unchanged pending the YAML-example review.


.. code:: bash
    
    # where to put results
    wdir: "." # no backslash at the end of the path
    # input
    infiles: "" # one undemultiplexed file or multiple demultiplexed files
    
    #SAMPLES
    experiment_groups: "" # txt file with group space sample per row
    experiment_group_file: ""
    seq_format: "-Q33" # -Q33 for Illumnina -Q64 for Sanger needed by fastX
    
    # barcodes
    barcodeLength: "" # if already demux = umi1_len
    minBaseQuality: 10
    umi1_len: "" # antisense of used barcodes --> this is the 3' UMI of the original barcode
    umi2_len: 0
    total_barcode_len: 0
    encode: False
    noBarcode_noUMI"
    experiment_type: "other" # one of "iCLIP", "iCLIP2", "iCLIP3", "eCLIP_5ntUMI", "eCLIP_10ntUMI", "eCLIP_ENCODE_5ntUMI", "eCLIP_ENCODE_10ntUMI", "miReCLIP", "noBarcode_noUMI" or "other" (if not "other" this will overwrite "barcodeLength", "umi1_len", "umi2_len", "total_barcode_len", "encode_umi")
    
    barcodes_fasta: "" # ! antisense of used barcodes, not needed if already demultiplexed
    quality_filter_barcodes: True # if no demultiplexing is done, should reads still be filtered for barcode / umi quality
    
    # demultiplexing
    demultiplex: False # Whether demultiplexing still has to be done; if FALSE, total_barcode_len should be 0, no barcode filtering will be done
    min_read_length: 15
    
    # adapter trimming
    adapter_file: ""
    adapter_cycles: 1
    adapter_trimming: True

    # 3'end trimming
    trim3: False
    trim3_len: 3
    
    # star alignment
    gtf: "" # has to be unzipped at the moment
    genome_fasta: "" # has to be unzipped or bgzip
    star_index: "" # optional prebuilt STAR index directory
    read_length: 150 
    outFilterMismatchNoverReadLmax: 0.04
    outFilterMismatchNmax: 999
    outFilterMultimapNmax: 1
    outReadsUnmapped: "Fastx"
    outSJfilterReads: "Unique"
    moreSTARParameters: ""
    
    # deduplicate
    deduplicate: True

Command-line examples are retained unchanged pending the dedicated example
review:

.. code:: bash

   racoon_clip crosslinks --configfile <your_configfile> --infiles <your_input_files> --barcodes-fasta <your_barcode_file.fasta>
   racoon_clip peaks --configfile <your_configfile> --infiles <your_input_files> --barcodes-fasta <your_barcode_file.fasta>

You can also check the command-line parameters with

.. code:: bash

   racoon_clip crosslinks -h
   racoon_clip peaks -h

.. note::

   If a parameter is specified in both the provided config file and the command line, the command line parameter will overwrite the config file.

racoon_clip will write a combined config file, containing the default options, where nothing was specified, the config file options and the command line options (command line parameters overwrite config file parameters) with the file ending "_updated.yaml" to keep track of the options you used.


Required and conditional input
------------------------------

Every analysis requires ``infiles`` and ``genome_fasta``. For
non-demultiplexed data, ``samples`` can be inferred from the input filenames;
an explicit value selects their order. Demultiplexing requires the expected
sample names and ``barcodes_fasta``.

A ``gtf`` annotation is optional. Either select an ``experiment_type`` preset
or define the barcode and UMI arrangement manually. The remaining parameters
use defaults unless the experiment requires a different value.

Input files and output directory
---------------------------------

- **wdir** (path): *default "./racoon_clip_out"*; Path where results are written to. A folder “results” containing all output will be created. Be aware that if a folder “results” already exists in this directory, it will be overwritten.

- **infiles** (path(s) to file(s)): One or multiple file paths to the fastq files of all samples. Multiple files should be provided in one string, separated by a space. When demultiplexing should be performed by racoon_clip, specify only one input fastq file of the multiplexed reads. FASTA files are not supported, as they will not allow any quality filtering.

- **seq_format** ("-Q33"/"-Q64"): *default "-Q33"*; Sequence format passed to FASTX-Toolkit. "-Q33" corresponds to data from an Illumina sequencer, "-Q64" would correspond to data from a Sanger sequencer.

Sample names and experiment groups
----------------------------------

- **samples** (string): Optional ordered sample names for non-demultiplexed
  inputs; required when demultiplexing. Names must agree with the resolved
  input names or barcode identifiers.
- **experiment_groups** (string): Legacy accepted setting. The current
  workflow resolves groups from ``experiment_group_file`` and does not use
  this value to filter or order them.
- **experiment_group_file** (path): Assigns samples to groups.

See :doc:`sample_groups` for the group-file format, default ``all_samples``
group, and singleton-group behavior.


Demultiplexing 
---------------------------------

Demultiplexing can be performed optionally. 

- **demultiplex** (True/False): *default False*; Whether demultiplexing still has to be done.
- **barcodes_fasta** (path to fasta): Path to fasta file with antisense sequences of used barcodes. Not needed if data is already demultiplexed. UMI sequences should be added as N. 

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

- **iCLIP3**: UMI of 9nt in the beginning (5' end)

- **eCLIP:** UMI of 10nt (or 5nt) in the beginning (5' end) of read2. This option can also be used for seCLIP data. 

- **eCLIP from ENCODE:** UMI of 10nt (or 5nt) in the beginning (5' end) of read2 is already trimmed off and stored in the read name

.. image:: ../CLIP_types.png
   :width: 600
   :alt: Common barcode and UMI arrangements


If your experiment used one of these setups, you can use the experiment_type parameter:

Using a standard barcode setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **experiment_type:** ("iCLIP"/"iCLIP2"/"iCLIP3"/"eCLIP_5ntUMI"/"eCLIP_10ntUMI"/"eCLIP_ENCODE_5ntUMI"/"eCLIP_ENCODE_10ntUMI"/"miReCLIP"
    /"noBarcode_noUMI"/"other"): *default: "other"*; The type of your experiment. 

.. Note::

   There are special types "eCLIP_ENCODE_5ntUMI" and "eCLIP_ENCODE_10ntUMI" because ENCODE data no longer has UMI information in the reads, but instead appends it to the end of the read names. If unsure if the data has a 5nt or 10nt UMI, check the read headers (for example, with head encode_sample.fastq)

Using manual barcode setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^
If your experiment does not follow one of these standard setups, you can define the setup manually and experiment_type defaults to other. To account for all of them and also allow other experimental setups, racoon_clip uses a barcode consisting of umi1+experimental_barcode+umi2. Parts of this barcode that do not exist in a particular data set can be set to length 0. These are the parameters to set up your barcode+UMI architecture manually:

- **barcodeLength** (int): length of the experimental barcode 

- **umi1_len** (int): length of UMI 1. Note that the sequences of the barcodes will be antisense of the barcodes used in the experiment. Therefore, UMI 1 is the 3' UMI of the experimental barcode. If the UMI is only 5' of the experimental barcode, set to 0. 

-  **umi2_len** (int): length of UMI 1. Note that the sequences of the barcodes will be antisense of the barcodes used in the experiment. Therefore, UMI 2 is the 5' UMI of the experimental barcode. If the UMI is only 3' of the experimental barcode, set to 0. 

- **total_barcode_len** (int): total length of the experimental barcode region that is read, including UMIs and random barcodes. Set to 0 if no barcode filtering should be done. 


For example, manually defining an iCLIP or eCLIP setup would look like this:

.. code-block:: yaml

   # iCLIP
   barcodeLength: 4
   umi1_len: 3
   umi2_len: 2
   total_barcode_len: 9

   # eCLIP
   barcodeLength: 0
   umi1_len: 10 (5)
   umi2_len: 0
   total_barcode_len: 10 (5)


Using manual barcode setup for ENCODE (or ENCODE-like) data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Note:: 

   This is needed for the older ENCODE eCLIP data where the UMI is only 5 nucleotides long

.. code-block:: yaml

   barcodeLength: 0 
   umi1_len: 10 (5)
   umi2_len: 0
   total_barcode_len: 10 (5)
   encode: True   

Quality filtering during barcode trimming
-----------------------------------------

- **min_read_length** (int): *default 15*; The minimum length a read should
  have after trimming barcodes, adapters, and UMIs. Shorter reads are removed.

- **quality_filter_barcodes** (True/False): *default True*; Whether reads should be filtered for a minimum sequencing quality in the barcode sequence. 

- **minBaseQuality** (int): *default 10*; The minimum per-base quality of the barcode region of each read. Reads below this threshold are filtered out. This only applies if quality_filter_barcodes is set to True. 

Adapters
-----------------
- **adapter_trimming** (True/False): *default True*; Whether adapter trimming should be performed. 

- **adapter_file** (path): *default /params.dir/adapters.fa*; A FASTA file of adapters that should be trimmed. The default file contains the Illumina Universal adapter, the Illumina Multiplexing adapter and 20 eCLIP adapters. 

- **adapter_cycles** (int): *default 1*; How many cycles of adapter trimming should be performed. We recommend using 1 for iCLIP and iCLIP2 data and 2 for eCLIP.

Additional trimming
-------------------

- **trim3** (True/False): *default False*; Trim bases from the 3-prime end.
  The iCLIP3 preset enables this behavior.
- **trim3_len** (int): *default 3*; Number of 3-prime bases to trim.

ENCODE read-name UMIs
---------------------

- **encode** (True/False): *default False*; Treat the UMI as already removed
  from the sequence and stored in the read name. Prefer an ENCODE
  ``experiment_type`` preset for standard data.
- **encode_umi_length** (int): *default 10*; Length of the UMI stored in an
  ENCODE-style read name.

Alignment to genome
---------------------------------

- **gft** (path): .gft file of the used genome annotation. Note that the file needs to be unzipped. (Can be obtained for example, from https://www.gencodegenes.org/human/.) 

- **genome_fasta** : .fasta file of the used genome annotation. Unzipped or bgzip files are supported. 

- **star_index** (path): *optional*; Path to a prebuilt STAR index directory. If provided, STAR will use this existing index instead of building a new one from genome_fasta and gtf. This can significantly speed up the alignment process for large genomes. If not specified or empty, STAR will build the index on-the-fly.

Parameters  passed to STAR:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
(Check the `STAR manual <https://physiology.med.cornell.edu/faculty/skrabanek/lab/angsd/lecture_notes/STARmanual.pdf>`_ for a detailed description.) 

- **read_length** (int): *default 150*; The length of the new sequencing reads.

- **outFilterMismatchNoverReadLmax** (ratio): *default 0.04*; Ratio of allowed mismatches during alignment. Of outFilterMismatchNoverReadLmax and outFilterMismatchNmax the more stringent setting will be applied. 

- **outFilterMismatchNmax** (int): *default 999*; Number of allowed mismatches during alignment. Of outFilterMismatchNoverReadLmax and outFilterMismatchNmax the more stringent setting will be applied. 

- **outFilterMultimapNmax** (int): *default 1*; Maximum number of allowed multimappers. 

- **outSJfilterReads**: *default "Unique"*

- **outReadsUnmapped**: *default "Fastx"*

- **moreSTARParameters**: Here all other STAR parameters can be passed.

Deduplication
--------------
- **deduplicate** (True/False): *default True*; Whether to perform deduplication. It is recommended to always use deduplication unless no UMIs are present in the data.

miR-eCLIP
---------

- **mir_genome_fasta** (path): Reference containing canonical mature miRNA
  sequences for the ``miReCLIP`` preset.
- **mir_starts_allowed** (string): *default "1 2 3 4"*; Accepted inferred
  positions at which the canonical miRNA begins in the processed read.
- **mir_5prime_missing_allowed** (string): *default "0 1 2 3"*; Accepted
  counts of missing canonical 5-prime miRNA bases.

See :doc:`tutorial_mir` for the processing model.

FastQ Screen
------------

- **fastqScreen** (True/False): *default False*; Enable contamination
  screening.
- **fastqScreen_config** (path): FastQ Screen configuration required when
  ``fastqScreen`` is enabled.

PureCLIP peak calling
---------------------

- **morePureclipParameters** (string): Additional options passed to PureCLIP
  by the ``peaks`` workflow. Restricting training to representative
  chromosomes can reduce memory use.


Execution parameters
--------------------
These parameters should be passed in the command line.

- ``--cores``: Number of cores for the execution.
- ``--verbose``: Print all commands of the process to the console.
- ``--log``: *default "racoon_clip.log"*; Name of log file.

Cluster profiles and scheduler-related Snakemake arguments are documented in
:doc:`cluster_execution`.
