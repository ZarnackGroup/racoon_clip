Tutorial: The miR-eCLIP module
================================

.. contents:: 
    :depth: 2


What is miR-eCLIP?
---------------------------

miR-eCLIP is a type of CLIP experiment that allows the mapping of microRNA binding sites on their target RNAs. 
During the experiment reverse transcription produces to a certain extent chimeric reads via read through. 
The chimeric reads consits of the miRNA seqeunce at the 5' end and the sequence of the target RNA next to the UV-crosslink. 
A detailed description of the miR-eCLIp experiment can be found `here <https://doi.org/10.1101/2022.02.13.480296>`_. 

.. figure:: ../mir-eCLIP.png
   :width: 300


How to analyse miR-eCLIP data with racoon_clip
-----------------------------

racoon_clip includes an option to analyse miR-eCLIP data (see below for a detailed description of the performed steps). For this some additional parameters need to be specified. Here is an example for a config file:

.. code:: python

    experiment_type: "miReCLIP"    
    
    # Where to put the results
    wdir: "output/path" # no backslash at the end of the path

    # Input
    infiles: "path/to/sample1.fastq path/to/sample2.fastq" # one un-demultiplexed file or multiple demultiplexed files

    # Samples
    samples: "sample1 sample2"

    # Annotation
    gtf: "path/to/annotation.gtf" # has to be unzipped at the moment
    genome_fasta: "path/to/genome_assembly.fa" # has to be unzipped or bgzip
    read_length: N 

    # Adapters
    adapter_cycles: 2
    
    # Chimeric miR
    mir_genome_fasta: "path/to/miR-genome.fasta" # for example from miRbase
    mir_starts_allowed: "0 1 2 3 4"



How does racoon_clip process miR-eCLIP data?
------------------------------------------

.. figure:: ../mir-eCLIP_racoon_schema.png
   :width: 300
