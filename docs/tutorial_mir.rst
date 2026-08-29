The miR-eCLIP module
====================

.. contents::
   :depth: 2
   :local:


What is miR-eCLIP?
------------------

miR-eCLIP is a CLIP experiment for mapping microRNA (miRNA) binding sites on
target RNAs. During reverse transcription, read-through from a miRNA into its
ligated target RNA produces chimeric reads. These reads contain the miRNA
sequence at the 5′ end, followed by sequence from the target RNA adjacent to
the UV crosslink.

A detailed description of the experiment is available in the
`miR-eCLIP publication <https://doi.org/10.1093/nar/gkae416>`_.

.. figure:: ../mir-eCLIP.png
   :width: 200px
   :align: center
   :alt: Overview of the miR-eCLIP experiment

   Overview of the miR-eCLIP experiment.


How to analyse miR-eCLIP data with racoon_clip
----------------------------------------------

racoon_clip includes a dedicated workflow for analysing miR-eCLIP data. Set
``experiment_type`` to ``miReCLIP`` and provide an uncompressed FASTA file
containing the mature miRNA reference sequences with ``mir_genome_fasta``.

The ``miReCLIP`` preset configures a 10-nucleotide UMI at the 5′ end of each
read. It sets ``barcodeLength``, ``umi1_len``, and ``total_barcode_len`` to
10 and enables the miR-eCLIP-specific workflow stages.

When demultiplexing is disabled, sample names are inferred by removing the
``.fastq``, ``.fq``, ``.fastq.gz``, or ``.fq.gz`` suffix from each input
filename. When demultiplexing is enabled, ``samples`` and
``barcodes_fasta`` must be specified explicitly.

Use absolute paths for FASTQ, reference, annotation, and output files. Some
workflow rules change their working directory before invoking external tools,
which makes relative input paths unreliable.


miR-eCLIP parameters
--------------------

``experiment_type``
   Set this to ``miReCLIP`` to enable the miR-eCLIP workflow and its
   predefined barcode and UMI arrangement.

``mir_genome_fasta``
   Absolute path to an uncompressed FASTA file containing mature miRNA
   reference sequences. RNA sequences containing ``U`` are converted to DNA
   sequences containing ``T`` before the Bowtie2 index is built.

``mir_starts_allowed``
   Space-separated inferred positions at which the canonical miRNA may begin
   in the processed read. The default is ``"1 2 3 4"``.

``mir_5prime_missing_allowed``
   Space-separated numbers of nucleotides that may be missing from the
   canonical miRNA 5′ end. The default is ``"0 1 2 3"``.

The standard input, genome, optional GTF annotation, adapter-trimming,
grouping, and STAR settings also apply. See :doc:`tutorial_customise` for
configuration guidance and :doc:`all_options` for the complete parameter
reference.


Example configuration
---------------------

.. code-block:: yaml

   # Experiment type
   experiment_type: "miReCLIP"

   # Output directory
   wdir: "/absolute/path/to/output"

   # Input FASTQ files
   # Multiple files are supplied as one space-separated string.
   infiles: "/absolute/path/to/sample1.fastq.gz /absolute/path/to/sample2.fastq.gz"

   # Genome reference and optional annotation
   genome_fasta: "/absolute/path/to/genome_assembly.fa"
   gtf: "/absolute/path/to/annotation.gtf"
   # Optionally provide an existing STAR index directory.
   star_index: ""
   read_length: 75

   # Adapter trimming
   adapter_cycles: 2

   # miRNA reference and filtering
   # For example, mature miRNA sequences obtained from miRBase.
   mir_genome_fasta: "/absolute/path/to/mature_miRNAs.fasta"
   mir_starts_allowed: "1 2 3 4"
   mir_5prime_missing_allowed: "0 1 2 3"


Processing overview
-------------------

The miR-eCLIP workflow first performs the standard racoon_clip preprocessing
steps, including barcode handling, quality filtering, and adapter trimming.

The first 24 nucleotides of each processed read are aligned to the supplied
miRNA reference. Reads that do not align continue through the standard
racoon_clip workflow. Among the aligned reads, only those satisfying the
configured canonical-start and missing-5′-nucleotide filters are retained as
chimeric reads. The canonical miRNA sequence is removed, and the remaining
target-RNA sequence is aligned to the genome.

Chimeric target-RNA alignments are deduplicated and used to identify
strand-specific, single-nucleotide crosslinks. The ``peaks`` workflow
additionally combines chimeric and non-chimeric alignments by experiment group
and calls peaks with PureCLIP.

The exact processing stages, filtering calculations, command-line options,
and external tools are described in :ref:`methods_mireclip`.


Outputs
-------

The miR-eCLIP workflow produces additional miRNA alignments, trimmed
target-RNA reads, chimeric genomic alignments, strand-specific crosslinks, and
a miRNA-specific HTML report.

The ``peaks`` workflow also produces group-level combined BAM files and
miR-eCLIP PureCLIP peaks.

See :doc:`tutorial_output` for the exact output paths, filenames, and
conditions under which each output is produced.
