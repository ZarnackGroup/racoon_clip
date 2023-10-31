Tutorial
================================

.. contents:: 
    :depth: 2


How to run racoon_clip
---------------------------

You can run racoon_clip with the following command:

.. code:: commandline

   racoon_clip run --configfile <your_configfile> --cores <n_cores> [OPTIONS]

How to pass parameters to racoon_clip
---------------------------

You can specify all parameters and options of racoon either directly in the command line or in a config file config.yaml file.

Here is a config file listing all default options:

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
    
    experiment_type: "other" # one of "iCLIP", "iCLIP2", "eCLIP_5ntUMI", "eCLIP_10ntUMI", "eCLIP_ENCODE_5ntUMI", "eCLIP_ENCODE_10ntUMI", "noBarcode_noUMI" or "other" (if not "other this will overwrite "barcodeLength", "umi1_len", "umi2_len", "exp_barcode_len", "encode_umi")
    
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

All these options can also be specified in the command line instead of the config file. For the command line parameters check out

.. code:: bash

   racoon_clip run -h


What you need to specify 
---------------------------

The following input parameters are required from the user:

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

Which steps will racoon_clip run by default?
---------------------------
This depends on the experiment_type. If not specified otherwise racoon_clip will run the following:

- **iCLIP,iCLIP2 and other:** Quality Control > Barcode and Adapter trimming > Alignment > Deduplication > Crosslink detection
- **eCLIP_5ntUMI and eCLIP_10ntUMI:** Quality Control > UMI and Adapter trimming > Alignment > Deduplication > Crosslink detection
- **"eCLIP_ENCODE_5ntUMI" and "eCLIP_ENCODE_10ntUMI":** Adapter trimming > Alignment > Deduplication > Crosslink detection
- **"noBarcode_noUMI":** Adapter trimming > Alignment > Crosslink detection




