All paramterets and options
================================

You can specify all parameters and options of racoon either directly in the commandline or in a configfile provided with

.. code:: commandline

   racoon_clip run .. --configfile [your_configfile]

To make your own config file you can start with an empthy .yaml file or copy one of the example config files here xx and save it to a .yaml file. Then adjust the parameters as needed.

In the commandline evry option can be specified by adding -- in front. For example:

.. code:: commandline
   racoon_clip run ..  --configfile [your_configfile] --infiles [your_input_files]

.. note::

   If a parameter is specified in both the provided configfile and the commandline, the commandline parameter will overwrite the configfile.

raccon_clip will write a combind configfile, containing the default option, where nothing was specified, the configfile options and the commandline options (commandline parameters overwrite configfile parameters) with the file ending "_updated.yaml" to keep track of the options you used.


Required input
---------------
The following input paramters are at minimum required from the user:

- infiles
- samples
- genome_fasta
- gtf
- either experiment_type or specific umi and barcode length (umi1_len, umi2_len, encode_umi_length, exp_barcode_len, barcodeLength)

See below for descriptions.

Input files and output directory
---------------------------------

- **wdir** (path): Path where results are written to. A folder “results” containing all output will be created. Be aware that in case a folder “results” already exists in this directory, it will be overwritten.

- **infiles** (path(s) to file(s)): One or multiple filepaths to the fastq files of all samples. Multiple files should be provided in one string separated by a space. When demultiplexing should be performed by racoon, specify only one input fastq of the multiplexed reads. At the moment fasta files are not supported, as they will not allow any quality filtering.

- **seq_format** ("-Q33"/"-Q64"): default "-Q33"; Sequence format passed to FASTX-Toolkit. "-Q33" corresponds to data from an Illumina sequencer, "-Q64" would correspond to data from a sanger sequencer.

Sample names 
---------------------------------

- **samples** (string): A list of all sample names. The names should be the same as the file names of the input files or in case of demultiplexing should be the same as specified in the barcode file. Sample names are split by one space. Example: "sample_1 sample_2", when the corresponding input files are names sample_1.fastq, and sample_2.fastq. 
- **experiment_groups** (string): In addition to sample-wise output, racoon will output merged bam and bw files. Which samples are merged together is specified by the experiment groups. Example: "WT KO". If all samples belong to the same condition, this can be left empthy and racoon_clip will automaticlly merge all samples. The groups must correspond to the group names specified in the experiment_group_file. 

- **experiment_group_file** (path to txt): A .txt file specifying which samples belong to which group. If all samples belong to the same condition, this can be left empthy and racoon_clip will automaticlly merge all samples.

.. Example:: 
   WT sample1
   WT sample2
   KO sample3
   KO sample4


Demultiplexing 
---------------------------------

Demultiplexing can optionally be performed. 

- **demuliplexing** (True/False): default False; Whether demultiplexing still has to be done.
- **barcodes_fasta** (path to fasta): Path to fasta file of antisense sequences of used barcodes. Not needed if data is already demultiplexed. UMI sequences should be added as N. 

.. parameters::
   >min_expamle_iCLIP_s1
   NNNGGTTNN
   >min_expamle_iCLIP_s2
   NNNGGCGNN

Barcodes, UMIs and adapters
---------------------------------

Different experimental approaches (iCLIP, iCLIP2, eCLIP) will use different lengths and positions for barcodes, UMIs, and adaptors. The following schematic shows the most common barcode set-ups. 

.. image:: ../experiment_types_schema.png
   :width: 600



If your experiment used one of these setups, you can use the expereriment_type parameter:

- **experiment_type** ("iCLIP"/"iCLIP2"/"eCLIP"/"eCLIP_ENCODE"/"other"): The type of your experiment. 

.. Note::
   There is a special type eCLIP_ENCODE, because ENCODE provided data has the UMI information no longer in the read, but appended to the end of the read names.


If your experiment does not follow one of these standard setups, you can define the setup manually and experiment_type defaults to other. In order to account for all of them an also allow other experimental setups racoon uses a barcode consiting of umi1+experimental_barcode+umi2 is used. Parts of this barcode that do not exist in a particular data set can be set to length 0. These are the parameters to manually set up your barcode+UMI architecture:

- **barcodeLength** (int): length of the complet barcode (UMI 1 + experimental barcode + UMI 2) 

- **umi1_len** (int): length of the UMI 1. Note that the sequences of the barcodes will be antisense of the barcodes used in the experiment. Therefore, UMI 1 is the 3' UMI of the experimental barcode. If the UMI is only 5' of the experimental barcode set to 0. 

-  **umi2_len** (int): length of the UMI 1. Note that the sequences of the barcodes will be antisense of the barcodes used in the experiment. Therefore, UMI 2 is the 5' UMI of the experimental barcode. If the UMI is only 3' of the experimental barcode set to 0. 

- **exp_barcode_len** (int): 0 if false exp_barcode_len should be 0, no bacode filtering will be done. 


For example manually defining an iCLIP setup manually would look like this:

iCLIP: 
^^^^^^

two UMI parts (3nt and 2nt) intersparced by the experimental barcode (4nt)
.. parameters::
   barcodeLength: 9
   umi1_len: 3
   umi2_len: 2
   exp_barcode_len: 4


iCLIP2: 
^^^^^^^

two UMI parts (5nt and 4nt) intersparced by the experimental barcode (6nt)

eCLIP:
^^^^^^^

barcode of 10nt (or 5nt) in the beginning (5' end) of read2 

barcodeLength: 10 (5)
umi1_len: 10 (5)
umi2_len: 0
exp_barcode_len: 0
` miR-eCLIP: barcode of 10nt in the beginning of read2 (same as eCLIP) `
barcodeLength: 10 (5)
umi1_len: 10 (5)
umi2_len: 0
exp_barcode_len: 0


quality filtering during barcode trimming:
---------------------------------

- **flexbar_minReadLength** (int): default 15; The minimun length a read should have after trimming of barcodes, adapters and UMIs. 

- **quality_filter_barcodes** (True/False): default True # Whether reads should be filtered for a minimum sequencing quality in the barcode sequence. 

- **minBaseQuality** (int): default 10; The minimum per base quality of the barcode region of each read. Reads below this threshold are filtered out. Only applies if quality_filter_barcodes is set to True. 

Adapters:
-----------------
- **adapter_trimming** (True/False): default True Whether adapter timming should be performed. 

- **adapter_file** (path): default /params.dir/adapters.fa A fasta file of adapters that should be trimmed. The default file contains the Illumina Universal adapter, the Illumina Multiplexing adapter and 20 eCLIP adapters. 

- **adapter_cycles** (int): default 1 How many cycles of adapter trimming should be performed. We recommend using 1 for iCLIP and iCLIP2 data and 2 for eCLIP (which is recommended in xxx for iCLIP and xxx for eCLIP).

### Alignment to genome
---------------------------------

- **gft** (path): .gft file of used genome annotation. Note, that the file needs to be unzipped. (Can be obtained for example from https://www.gencodegenes.org/human/.) 

- **genome_fasta** : .fasta file of used genome annotation. Unzipped or bgzip files are supported. 

parameters  passed to STAR:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
(Check STAR manual for a detailed description (https://physiology.med.cornell.edu/faculty/skrabanek/lab/angsd/lecture_notes/STARmanual.pdf)) 

- **sjdbOverhang** (int): default 99 # readlength -1 - barcodelength - adapter much faster tospecify than to calculated from fastq file. 

- **outFilterMismatchNoverReadLmax** (ratio) : default 0.04 Ratio of allowed mismatches during alignment. Of outFilterMismatchNoverReadLmax and outFilterMismatchNmax the more stringent setting will be applied. 

- **outFilterMismatchNmax** (int): default 999; Number of allowed mismatches during alignment. Of outFilterMismatchNoverReadLmax and outFilterMismatchNmax the more stringent setting will be applied. 

- **outFilterMultimapNmax** (int): default 1; Maximum number of allowed multimapping. 

- **outSJfilterReads**: default "Unique"

