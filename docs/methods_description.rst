Detailed description of steps performed by racoon
=================================================

.. contents::   
    :depth: 2

Quality filtering 
^^^^^^^^^^^^^^^^^^
Sequencing reads are filtered for a Phred score >= 10 inside the unique molecular identifier (UMI) at positions 1-10 of each read to ensure reliable sample and duplicate assignment. The cutoff can be changed by specifiing an other value by the racoon_clip *minBaseQuality* option.

Demultiplexing, UMI & Adapter trimming
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Demultiplexing and 3’ adapters adapter trimming are performed with FLEXBAR (version 3.5.0). FLEXBAR also handles UMIs and trimms barcodes.

If demulitplexing is turned on, this is done with the FLEXBAR via the provided barcode_fasta with FLEXBAR parameters ``--barcodes {input.barcodes} --barcode-unassigned --barcode-error-rate 0``.

3’ adapters adapters are trimmed using FLEXBAR options ``--adapter-trim-end RIGHT --adapter-error-rate 0.1 --adapter-min-overlap 1 --adapter-cycles <as specified>`` by default, but adapter trimming can also be turned off.

At the same time, UMIs (and barcodes, if present) are trimmed from the 5’ end of the reads and stored in the read names using FLEXBAR options ``--umi-tags --barcode-trim-end LTAIL``. 

Reads that are shorter than 15 nt after trimming are discarded using FLEXBAR option ``--min-read-length 15``. The cutoff can be changed by specifiing an other value by the racoon_clip *flexbar_minReadLength* option.

See also: `FLEXBAR—Flexible Barcode and Adapter Processing for Next-Generation Sequencing Platforms <https://www.mdpi.com/2079-7737/1/3/895>`_. 

Genome alignment 
^^^^^^^^^^^^^^^^
Reads are aligned to the specified genome with STAR (version 2.7.10). In short, the genome is indexed with ``STAR –runMode genomeGenerate``. Then, the reads of each sample are individually aligned to the genome with ``STAR –runMode alignReads --sjdbOverhang 139 --outFilterMismatchNoverReadLmax 0.04 --outFilterMismatchNmax 999 --outFilterMultimapNmax 1 --alignEndsType "Extend5pOfRead1" --outReadsUnmapped "Fastx" --outSJfilterReads "Unique"``. Obtained bam files are indexed with samtools index (version xx). All parameters except ``--alignEndsType "Extend5pOfRead1"`` can be changed via racoon options.

See also:

- `STAR: ultrafast universal RNA-seq aligner <https://academic.oup.com/bioinformatics/article/29/1/15/272537>`_
- `The Sequence Alignment/Map format and SAMtools <https://academic.oup.com/bioinformatics/article/25/16/2078/204688>`_

Deduplication
^^^^^^^^^^^^^^
Aligned reads were deduplicated with ``umi_tools dedup --extract-umi-method read_id --method unique`` (UMI-tools version 1.1.1).

See also `UMI-tools: modeling sequencing errors in Unique Molecular Identifiers to improve quantification accuracy <https://genome.cshlp.org/content/27/3/491>`_

Assignment of crosslink sites of CLIP reads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The deduplicated bam files are converted into bed files using bedtools bamtobed (version 2.30.0). The reads were the shifted by 1 nt upstream with bedtools shift -m 1 -p -1 because the UV crosslink sites should be positioned 1 nt upstream of the eCLIP read starts. The bed files were split into plus and minus strand, and the reads were then reduced to 1-nt crosslink events using awk.
To allow for visualization, the bed files of 1 nt events were converted to bigWig files using bedGraphToBigWig (ucsc-bedgraphtobigwig version 377). Additionally, the bigWig files of replicates were merged by groups with bigWigMerge (ucsc-bigwigmerge version 377).

See also:

- `BEDTools: a flexible suite of utilities for comparing genomic features <https://academic.oup.com/bioinformatics/article/26/6/841/244688>`_
- `UCSC tools <https://github.com/ucscGenomeBrowser/kent>`_
