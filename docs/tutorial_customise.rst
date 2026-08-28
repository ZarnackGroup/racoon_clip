.. _tutorial_customise:

Configuration and experiment types
==================================

RaccoonClip accepts workflow settings from a YAML configuration file and from
command-line options. Configuration-file keys use their exact names, including
underscores and capitalization. When the same setting is provided in both
places, the command-line value takes precedence.

The complete parameter reference is :doc:`all_options`. This page explains
how the main choices fit together.

Existing default configuration example
--------------------------------------

This existing block is retained unchanged pending the YAML-example review.

.. code:: yaml

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
    umi1_len: "" # antisense of used barcodes --> this is the 3' UMI of the original barcode
    umi2_len: 0
    total_barcode_len: 0
    encode: False

    experiment_type: "other" # one of "iCLIP", "iCLIP2", "iCLIP3", "eCLIP_5ntUMI", "eCLIP_10ntUMI", "eCLIP_ENCODE_5ntUMI", "eCLIP_ENCODE_10ntUMI", "miReCLIP","noBarcode_noUMI" or "other" (if not "other this will overwrite "barcodeLength", "umi1_len", "umi2_len", "total_barcode_len", "encode_umi")

    barcodes_fasta: "" # ! antisense of used barcodes, not needed if already demultiplexed
    quality_filter_barcodes: True # if no demultiplexing is done, should reads still be filtered for barcode / umi quality

    # demultiplexing
    demultiplex: False # Whether demultiplexing still has to be done; if FALSE, total_barcode_len should be 0, and no barcode filtering will be done
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

Experiment presets
------------------

The ``experiment_type`` setting applies a known barcode and UMI arrangement.
Supported values are:

- ``iCLIP``
- ``iCLIP2``
- ``iCLIP3``
- ``eCLIP_5ntUMI``
- ``eCLIP_10ntUMI``
- ``eCLIP_ENCODE_5ntUMI``
- ``eCLIP_ENCODE_10ntUMI``
- ``miReCLIP``
- ``noBarcode_noUMI``
- ``other``

Use an ENCODE preset when the UMI has already been removed from the read and
stored in its name. Use ``noBarcode_noUMI`` when neither barcode nor UMI
sequence remains. Use ``other`` with explicit barcode and UMI lengths for a
custom design.

.. image:: ../CLIP_types.png
   :width: 600
   :alt: Common barcode and UMI arrangements

   Common barcode and UMI arrangements.

Samples and groups
------------------

``samples`` identifies the reads processed as separate samples.
``experiment_group_file`` and ``experiment_groups`` control group-level
merging and peak calling. See :doc:`sample_groups` for the assignment format
and validation behavior.

Optional processing stages
--------------------------

``quality_filter_barcodes``
   Filter reads using sequencing quality in the barcode or UMI region.

``demultiplex``
   Split one multiplexed input according to ``barcodes_fasta``.

``adapter_trimming``
   Trim adapters with FLEXBAR. ``adapter_cycles`` controls repeated trimming.

``trim3``
   Trim a configured number of bases from the 3-prime end. This is enabled
   automatically for the iCLIP3 preset.

``deduplicate``
   Deduplicate aligned reads by UMI. The no-barcode/no-UMI preset disables
   UMI-based deduplication.

Alignment choices
-----------------

``genome_fasta`` supplies the reference sequence. A ``gtf`` annotation is
optional; without it, STAR aligns without annotated splice junctions.
``star_index`` can point to an existing STAR index. Otherwise, the workflow
builds an index for the run.

STAR tuning parameters include ``outFilterMismatchNoverReadLmax``,
``outFilterMismatchNmax``, ``outFilterMultimapNmax``,
``outReadsUnmapped``, ``outSJfilterReads``, and
``moreSTARParameters``. Consult the
`STAR manual <https://github.com/alexdobin/STAR/blob/master/doc/STARmanual.pdf>`_
before changing them.

Peak calling
------------

The ``peaks`` workflow runs PureCLIP after group BAM creation.
``morePureclipParameters`` passes additional PureCLIP options. Limiting model
training to representative chromosomes can reduce memory requirements for
large genomes.

FastQ Screen
------------

The configuration keys ``fastqScreen`` and ``fastqScreen_config`` enable the
optional contamination-screening path. A readable FastQ Screen configuration
is required when the feature is enabled.

Execution environments
----------------------

For scheduler profiles and forwarded Snakemake arguments, see
:doc:`cluster_execution`. For bind mounts and in-container paths, see
:doc:`tutorial_container`.
