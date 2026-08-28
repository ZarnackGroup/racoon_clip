.. _tutorial:

Quickstart
==========

This page shows the shortest route from an installed package to a first
analysis. For explanations of experiment types and optional processing
stages, continue with :doc:`tutorial_customise`.

Choose the workflow
-------------------

Use ``crosslinks`` when the required result is a set of single-nucleotide
crosslink tracks. Use ``peaks`` when group-level PureCLIP peak calling should
run after crosslink identification.

.. code:: commandline

   racoon_clip crosslinks --configfile <your_configfile.yaml> --cores <n_cores> [OPTIONS]
   racoon_clip peaks --configfile <your_configfile.yaml> --cores <n_cores> [OPTIONS]

Prepare a minimal configuration
-------------------------------

The following existing example is intentionally retained unchanged pending
the configuration-example review described in the documentation update plan.

.. code:: yaml

    # where to put results
    wdir: "output/path" # no backslash at the end of the path
    # input
    infiles: "path/to/sample1.fastq path/to/sample2.fastq" # one un-demultiplexed file or multiple demultiplexed files
    samples: "sample1 sample2"
    # annotation
    gtf: "path/to/annotation.gtf" # has to be unzipped at the moment
    genome_fasta: "path/to/genome_assembly.fa" # has to be unzipped or bgzip
    star_index: "" # optional prebuilt STAR index directory
    read_length: N

    # experiment type
    experiment_type: "iCLIP"/"iCLIP2"/"iCLIP3"/"eCLIP_5ntUMI"/"eCLIP_10ntUMI"/"eCLIP_ENCODE_5ntUMI"/"eCLIP_ENCODE_10ntUMI"/"miReCLIP"/"noBarcode_noUMI"/"other"

    # for the demultiplexing functionality or for data with experiment_type "iCLIP", "iCLIP2", or "iCLIP3"
    barcodes_fasta: "path/to/barcodes.fasta" # barcodes need to have the same names as specified in the samples parameter above

    # peakcalling setting (recommended)
    morePureclipParameters: "-iv 'chr1;chr2;chr3;'"

Run and inspect
---------------

Run one of the commands above from the repository or analysis directory.
RaccoonClip writes a merged ``*_updated.yaml`` configuration next to the
provided configuration file. Keep this file with the results because it
records the defaults, file settings, and command-line overrides used for the
run.

See :doc:`tutorial_output` for result interpretation and
:doc:`troubleshooting` for common startup errors.
