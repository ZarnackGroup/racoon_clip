# racoon_clip - User manual

racoon_clip processes your iCLIP and eCLIP data from raw files to single-nucleotide crosslinks in a single step. It is an automatition of the iCLIP pipeline pubished by Busch et al. 2020 ([iCLIP data analysis: A complete pipeline from sequencing reads to RBP binding sites] (https://doi.org/10.1016/j.ymeth.2019.11.008)) making the same processing now availabe for both iCLIP and eCLIP data in a highly reproducible manner. 

The performed steps are an optional quality filter, optional demultiplaexing, adapter trimming, genome alignment, optional deduplication and selection of single nucleotide crosslinks.

![](Workflow.pdf)


xx detailed methods steps here or later?

## Installation


### from Docker
xx

### from GitHub

Download the zip file of your prefered release from github and unzip it. Then go into the unziped folder.

```
unzip racoon_clip-1.0.0.zip
cd racoon_clip-1.0.0
```
It is recommended to install racoon_clip it a fresh conda enviroment.

```
conda create -n racoon_clip pip
conda activate racoon_clip
```
The install racoon with pip.
```
pip install --user -e .
```

You can now check the installation by running help option or a minimal example.

```
racoon_clip -h
```



## Usage
Once installed you can run racoon with
```
racoon --cores [number_of_cores] --configfile [/path/to/config/file.yaml]
```
### Minimal examples




## Config file
Information on input data, used annotation, the output directory, and user options are passed to raccoon via a config file in .yaml format. Please find a description of all parameters in the config file below.
To make your own config file you can copy the following default config file and save it to a .yaml file. Then adjust the parameters as needed.
```
# where to put results
wdir: ""
# input
indir: "" # for multiple files after demultiplexing
infile: "" # one un-demultiplexed file
gz: True
seq_format: "-Q33" # -Q33 for Illumnina -Q64 for Sanger needed by FastX

#SAMPLES
samples: ""
experiment_group_file: "" # txt file with group space sample per row
experiment_groups: ""


# barcodes
barcodeLength: 10 # if already demux = umi1_len
barcodeLength.read1: 0  # in paired end eCLIP data
minBaseQuality: 10
umi1_len: 10 # antisense of used barcodes --> this is the 3' umi of the original barcode
umi2_len: 0
exp_barcode_len: 0


barcodes_fasta: "" # ! antisense of used barcodes, not needed if already demultiplexed
quality_filter_barcodes: True # if no demultiplexing is done, is there still a barcode

# demultiplexing
demuliplexing: False # Whether demultiplexing still has to be done, if FALSE exp_barcode_len should be 0, no bacode filtering will be done
flexbar_minReadLength: 15

#adapter adapter_trimming
adapter_file: ""
adapter_cycles: 1
adapter_trimming: True

# star alignment
paired: False
gft: "" # has to be unzipped at the moment
genome_fasta: "" # has to be unzipped or bgzip
sjdbOverhang: 139 # readlength -1 - barcode-length - adapter much faster to specify than to calculate from fastq file
outFilterMismatchNoverReadLmax: 0.04
outFilterMismatchNmax: 999
outFilterMultimapNmax: 1
alignEndsType: "Extend5pOfRead1"
outReadsUnmapped: "Fastx"
outSJfilterReads: "Unique"

# chimeric miR
miR: False
miR_genome_fasta: ""
miR_starts_allowed: "1 2 3 4"
```

### Input files and output directory
* ***wdir*** (path): Path where results are written to. A folder “results” containing all output will be created. Be aware that in case a folder “results” already exists in this directory, it will be overwritten.
* ***indir*** (path) or ***infile*** (path to file): indir should specify one folder that contains the input fastq files of all samples. When demultiplexing should be performed by racoon, indir should be left empty and instead infile should specify the multiplexed fastq file. At the moment fasta files are not supported, as they will not allow any quality filtering.
* ***gz*** (True/False): *default True*; Whether the input file(s) are in .gz format or unzipped.
* ***seq_format*** ("-Q33"/"-Q64"): *default "-Q33"*; Sequence format passed to FASTX-Toolkit. "-Q33" corresponds to data from an Illumina sequencer, "-Q64" would correspond to data from a sanger sequencer.

### Sample names
* ***samples*** (string): A list of all sample names. The names should be the same as the file names of the input files or in case of demultiplexing should be the same as specified in the barcode file. Sample names are split by one space. Example: "sample_1 sample_2", when the corresponding input files are names sample_1.fastq, and sample_2.fastq.
* ***experiment_groups*** (string): In addition to sample-wise output, racoon will output merged bam and bw files. Which samples are merged together is specified by the experiment groups. Example: "WT KO". If all samples belong to the same condition, specify only one group. Example: "All". The groups must correspond to the group names specified in the experiment_group_file.
* ***experiment_group_file*** (path to txt): A .txt file specifying which samples belong to which group. Example:
```
WT sample1
WT sample2
KO sample3
```

### Demultiplexing
Demultiplexing can optionally be performed. At the moment this only works for single-stranded data.
* ***demuliplexing*** (True/False): *default False*; Whether demultiplexing still has to be done.
* ***barcodes_fasta*** (path to fasta): Path to fasta file of antisense sequences of used barcodes. Not needed if data is already demultiplexed. UMI sequences should be added as N. Example: 
```
>min_expamle_iCLIP_s1
NNNGGTTNN
>min_expamle_iCLIP_s2
NNNGGCGNN
```
### Barcodes, UMIs and adapters
Different experimental approaches (iCLIP, iCLIP2, eCLIP) will use different lengths and positions for barcodes, UMIs, and adaptors (see schemes below). In order to account for all of them an also allow other experimental setups racoon uses a barcode consiting of umi1+experimental_barcode+umi2 is used. Parts of this barcode that do not exist in a particular data set can be set to length 0. These are the most common combinations:
xxx graf scheme

iCLIP: two UMI parts (3nt and 2nt) intersparced by the experimental barcode (4nt)
```
barcodeLength: 9
umi1_len: 3 
umi2_len: 2
exp_barcode_len: 4
```
iCLIP2:  two UMI parts (5nt and 4nt) intersparced by the experimental barcode (6nt)

eCLIP: barcode of 10nt (or 5nt) in the beginning (5' end) of read2
```
barcodeLength: 10 (5)
umi1_len: 10 (5)
umi2_len: 0
exp_barcode_len: 0
```
miR-eCLIP: barcode of 10nt in the beginning of read2 (same as eCLIP)
```
barcodeLength: 10 (5)
umi1_len: 10 (5)
umi2_len: 0
exp_barcode_len: 0
```
* ***barcodeLength*** (int): length of the complet barcode (UMI 1 + experimental barcode + UMI 2)
* ***umi1_le***n (int): length of the UMI 1. Note that the sequences of the barcodes will be antisense of the barcodes used in the experiment. Therefore, UMI 1 is the 3' UMI of the experimental barcode. If the UMI is only 5' of the experimental barcode set to 0.
* ***umi2_len*** (int): length of the UMI 1. Note that the sequences of the barcodes will be antisense of the barcodes used in the experiment. Therefore, UMI 2 is the 5' UMI of the experimental barcode. If the UMI is only 3' of the experimental barcode set to 0.
* ***exp_barcode_len*** (int): 0 if false exp_barcode_len should be 0, no bacode filtering will be done. barcodeLength.read1: 0 # in paired end eCLIP data

quality filtering during barcode trimming:
* ***flexbar_minReadLength*** (int): *default 15*; The minimun length a read should have after trimming of barcodes, adapters and UMIs.
* ***quality_filter_barcodes*** (True/False): *default True* # Whether reads should be filtered for a minimum sequencing quality in the barcode sequence.
* ***minBaseQuality*** (int): *default 10*; The minimum per base quality of the barcode region of each read. Reads below this threshold are filtered out. Only applies if quality_filter_barcodes is set to True.
Adapter setting:
* ***adapter_trimming*** (True/False): *default True* Whether adapter timming should be performed.
* ***adapter_file*** (path): *default /params.dir/adapters.fa* A fasta file of adapters that should be trimmed. The default file contains the Illumina Universal adapter, the Illumina Multiplexing adapter and 20 eCLIP adapters.
* ***adapter_cycles*** (int): *default 1* How many cycles of adapter trimming should be performed. We recommend using 1 for iCLIP and iCLIP2 data and 2 for eCLIP and mir-eCLIP data (which is recommended in xxx for iCLIP and xxx for eCLIP).

### Alignment to genome
* ***paired*** (True/False): *default False* Whether data is paired-end
* ***gft*** (path): .gft file of used genome annotation. Note, that the file needs to be unzipped. (Can be obtained for example from https://www.gencodegenes.org/human/.)
* ***genome_fasta***: .fasta file of used genome annotation. Unzipped or bgzip files are supported.
parameter passed to STAR: (Check STAR manual for a detailed description (https://physiology.med.cornell.edu/faculty/skrabanek/lab/angsd/lecture_notes/STARmanual.pdf))
* ***sjdbOverhang*** (int): *default 99* # readlength -1 - barcodelength - adapter much faster tospecify than to calculated from fastq file
* ***outFilterMismatchNoverReadLmax*** (ratio) : *default 0.04* Ratio of allowed mismatches during alignment. Of outFilterMismatchNoverReadLmax and outFilterMismatchNmax the more stringent setting will be applied.
* ***outFilterMismatchNmax*** (int): *default 999*; Number of allowed mismatches during alignment. Of outFilterMismatchNoverReadLmax and outFilterMismatchNmax the more stringent setting will be applied.
* ***outFilterMultimapNmax*** (int): *default 1*; Maximum number of allowed multimapping.
* ***outSJfilterReads***: *default "Unique"*

### miR-eCLIP settings
racoon can also process miR-eCLIP data. If you have miR-eCLIP data please specify these additional parameters in the configfile:
* ***miR*** (True/False): *default False*; Set to true, if your data comes from a miR-eCLIP experiment.
* ***miR_genome_fasta*** (path): .fasta file of the annotation of mature miRs that should be used. (Can be obtained for example from (https://www.mirbase.org/ftp.shtml))
* ***miR_starts_allowed***: *default "1 2 3 4"*

### Examples
xx

### Memory requirements
xx
