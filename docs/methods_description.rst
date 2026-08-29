.. _methods_description:

Detailed description of steps performed by racoon_clip
=======================================================

.. contents::
   :depth: 2
   :local:

Quality control
---------------
Basic quality controls are performed several times throughout the workflow using FastQC (v0.12.1), MultiQC (v.1.31). Optionally, FastQ Screen (v0.15.3) can run using a custom FastQ Screen config file.

Quality filtering (Optional)
----------------------------
Sequencing reads can be filtered for a Phred score >= 10 inside the unique molecular identifier (UMI) at positions 1-10 of each read to ensure reliable sample and duplicate assignment. The cutoff can be changed by specifying another value by the racoon_clip *minBaseQuality* option.

Demultiplexing, UMI & Adapter trimming
---------------------------------------
Demultiplexing and 3’ adapters adapter trimming are performed with FLEXBAR (version 3.5.0). FLEXBAR also handles UMIs and trims barcodes.

If demultiplexing is turned on, this is done with the FLEXBAR via the provided barcode_fasta with FLEXBAR parameters ``--barcodes {input.barcodes} --barcode-unassigned --barcode-error-rate 0``.

3’ adapters are trimmed using FLEXBAR options ``--adapter-trim-end RIGHT --adapter-error-rate 0.1 --adapter-min-overlap 1 --adapter-cycles <as_specified>`` by default, but adapter trimming can also be turned off.

At the same time, UMIs (and barcodes, if present) are trimmed from the 5’ end of the reads and stored in the read names using FLEXBAR options ``--umi-tags --barcode-trim-end LTAIL``. 

For iCLIP3, or when the parameter **trim3** True is used, a number of nucleotides is trimmed of the 3'end of the reads (default 3) with FLEXBAR  ``--zip-output GZ -y 3 --min-read-length 15``. This is necessary for iCLIP3, which uses a second 3nt-long UMI at the 3' end.

Reads that are shorter than 15 nt after trimming are discarded using the FLEXBAR option ``--min-read-length 15``. The cutoff can be changed by specifying another value with the racoon_clip *flexbar_minReadLength* option.

See also: `FLEXBAR—Flexible Barcode and Adapter Processing for Next-Generation Sequencing Platforms <https://www.mdpi.com/2079-7737/1/3/895>`_. 

Genome alignment
----------------
Reads are aligned to the specified genome with STAR (version 2.7.10). In short, the genome is indexed with ``STAR –runMode genomeGenerate``. Then, the reads of each sample are individually aligned to the genome with ``STAR –runMode alignReads --sjdbOverhang 139 --outFilterMismatchNoverReadLmax 0.04 --outFilterMismatchNmax 999 --outFilterMultimapNmax 1 --alignEndsType "Extend5pOfRead1" --outReadsUnmapped "Fastx" --outSJfilterReads "Unique"``. Obtained bam files are indexed with SAMtools index (version 1.11). All parameters except ``--alignEndsType "Extend5pOfRead1"`` can be changed via racoon_clip options.

See also:

- `STAR: ultrafast universal RNA-seq aligner <https://academic.oup.com/bioinformatics/article/29/1/15/272537>`_
- `The Sequence Alignment/Map format and SAMtools <https://academic.oup.com/bioinformatics/article/25/16/2078/204688>`_

Deduplication
-------------
Aligned reads are deduplicated with ``umi_tools dedup --extract-umi-method read_id --method unique`` (UMI-tools version 1.1.1).

See also `UMI-tools: modelling sequencing errors in Unique Molecular Identifiers to improve quantification accuracy <https://genome.cshlp.org/content/27/3/491>`_

Assignment of crosslink sites of CLIP reads
-------------------------------------------
The deduplicated bam files are converted into bed files using bedtools bamtobed (version 2.30.0). The reads are shifted by 1 nt upstream with bedtools shift -m 1 -p -1 because the UV crosslink sites should be positioned 1 nt upstream of the eCLIP read starts. The bed files are split into plus and minus strands, and the reads are then reduced to 1-nt crosslink events using awk.
To allow for visualization, the bed files of 1 nt events are converted to bigWig files using bedGraphToBigWig (ucsc-bedgraphtobigwig version 377). Additionally, the bigWig files of replicates are merged by groups with bigWigMerge (ucsc-bigwigmerge version 377).

See also:

- `BEDTools: a flexible suite of utilities for comparing genomic features <https://academic.oup.com/bioinformatics/article/26/6/841/244688>`_
- `UCSC tools <https://github.com/ucscGenomeBrowser/kent>`_


Peak calling
------------
Peaks are called with PureCLIP on the merged bam files from each group.

See also: `PureCLIP: capturing target-specific protein–RNA interaction footprints from single-nucleotide CLIP-seq data <https://genomebiology.biomedcentral.com/articles/10.1186/s13059-017-1364-2>`_


.. _methods_mireclip:

miR-eCLIP-specific processing
-----------------------------

The miR-eCLIP workflow separates miRNA-containing chimeric reads from
non-chimeric reads and processes both read classes through the appropriate
alignment and crosslink-identification steps.

.. figure:: ../mir-eCLIP_racoon_schema.png
   :width: 300px
   :align: center
   :alt: Processing of miR-eCLIP data by racoon_clip

   Processing of miR-eCLIP data by racoon_clip.


Quality filtering and adapter trimming
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The standard barcode handling, quality filtering, and adapter trimming steps
are applied first. The miR-eCLIP-specific rules operate on the resulting
adapter-trimmed reads. For multiplexed input, the workflow instead uses the
reads produced by the combined demultiplexing and adapter-trimming step.


Preparing the miRNA reference
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The FASTA file supplied with ``mir_genome_fasta`` contains the mature miRNA
reference sequences. If the sequences contain uracil (``U``), racoon_clip
converts it to thymine (``T``) before building a Bowtie2 index with
``bowtie2-build``.


miRNA alignment
^^^^^^^^^^^^^^^

Filtered and trimmed reads are shortened to the first 24 nucleotides at their
5′ ends with:

.. code-block:: text

   fastx_trimmer -l 24

For chimeric reads, this region is expected to contain the mature miRNA
sequence. Using shortened reads improves alignment to the short mature-miRNA
reference sequences.

The shortened reads are aligned to the miRNA reference with Bowtie2 using:

.. code-block:: text

   --local -D 20 -R 3 -L 10 -i S,1,0.50 -k 20 --norc --trim5 2


Separating chimeric and non-chimeric reads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The resulting SAM records are separated according to the SAM unmapped flag.
``samtools view -F 4`` retains reads aligned to the miRNA reference, which are
treated as candidate chimeric reads. ``samtools view -f 4`` retains reads that
did not align to the miRNA reference, which are treated as non-chimeric reads.

The identifiers of the unaligned reads are used to recover the complete
non-chimeric sequences from the quality-filtered and trimmed FASTQ files with
``seqkit grep -n``. The recovered FASTQ files are sorted by read name with
``seqkit sort -n`` and passed to the standard genomic-alignment workflow.


Identifying and removing the canonical miRNA
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For each primary miRNA alignment, racoon_clip infers where the canonical
miRNA begins in the original processed read. This calculation accounts for
the two bases removed with Bowtie2's ``--trim5 2`` option, leading soft
clipping in the CIGAR string, and the alignment start on the miRNA reference.
``mir_starts_allowed`` determines which inferred start positions are
accepted.

The start of the target-RNA portion is calculated using the complete
canonical length of the aligned miRNA sequence in ``mir_genome_fasta``.
``mir_5prime_missing_allowed`` determines how many missing nucleotides from
the canonical miRNA 5′ end are accepted. Insertions and deletions are
projected through the CIGAR string when the target-RNA start is calculated.

The miRNA name is prepended to the read identifier. The canonical miRNA
portion is then removed from the sequence and its quality string before the
target-RNA portion is written to FASTQ.


Genomic alignment of chimeric reads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If ``star_index`` is not supplied, racoon_clip builds a STAR index from
``genome_fasta`` and the optional ``gtf`` annotation. The target-RNA portions
of the chimeric reads are aligned to the genome with
``STAR --runMode alignReads``. The resulting BAM files are coordinate-sorted
by STAR and indexed with ``samtools index``.


Deduplication of chimeric reads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The chimeric target-RNA alignments are deduplicated with:

.. code-block:: text

   umi_tools dedup --extract-umi-method read_id --method unique

The current miR-eCLIP workflow uses these deduplicated chimeric BAM files for
crosslink extraction and group-level processing. The ``deduplicate`` setting
controls the standard non-chimeric branch but does not currently disable
deduplication of the chimeric branch.


Identifying chimeric crosslinks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The deduplicated chimeric BAM files are converted to BED format with
``bedtools bamtobed``. The intervals are shifted by one nucleotide in the
strand-aware 5′ direction with:

.. code-block:: text

   bedtools shift -m 1 -p -1

This places the inferred UV crosslink one nucleotide before the end of the
target-RNA portion of the read. The miRNA name stored in the read identifier
is retained in the BED record. Records are separated by strand and reduced to
one-nucleotide crosslink positions, using the left edge on the plus strand and
the right edge on the minus strand.

For visualisation in a genome browser, the strand-specific crosslink counts
are converted to BigWig files with ``bedGraphToBigWig``. BigWig files are
combined by resolved experiment group with ``bigWigMerge``. For a group
containing only one sample, the sample-level files are reused directly.


miR-eCLIP peak calling
^^^^^^^^^^^^^^^^^^^^^^

This stage is run only by ``racoon_clip peaks``. Deduplicated chimeric
target-RNA BAM files are first combined by resolved experiment group. Each
group-level chimeric BAM is then merged with the corresponding group-level
non-chimeric BAM.

The combined BAM file is sorted, indexed, and supplied to PureCLIP. See
:doc:`tutorial_output` for the resulting paths and filenames.
