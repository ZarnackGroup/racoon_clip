Detailed description of steps performed by racoon
=================================================

.. contents:: ""
    :depth: 2

Quality filtering 
^^^^^^^^^^^^^^^^^^
Sequencing reads are filtered for a Phred score >= 10 inside the unique molecular identifier (UMI) at positions 1-10 of each read to ensure reliable sample and duplicate assignment. 

Demultiplexing, UMI & Adapter trimming
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
3’ adapters (Illumina Universal Adapter, Illumina Multiplexing Adapter, and eCLIP adapters 1-20) were trimmed with FLEXBAR (version 3.5.0) 53 using two cycles (--adapter-trim-end RIGHT --adapter-error-rate 0.1 --adapter-min-overlap 1 --adapter-cycles 2). At the same time, UMIs were trimmed from the 5’ end of the reads and stored in the read names (--umi-tags --barcode-trim-end LTAIL). Reads that were shorter than 15 nt after trimming were discarded (--min-read-length 15).

Genome alignment 
^^^^^^^^^^^^^^^^
Regular eCLIP reads and trimmed chimeric reads were aligned to the mouse genome (version GRCm38.p6) using GENCODE gene annotation version M23, CHR 58 with STAR (version 2.7.10, 59. In short, the genome was indexed with STAR –runMode genomeGenerate. Then, the regular and chimeric eCLIP reads of each sample were individually aligned to the genome with STAR –runMode alignReads (--sjdbOverhang 139 --outFilterMismatchNoverReadLmax 0.04 --outFilterMismatchNmax 999 --outFilterMultimapNmax 1 --alignEndsType "Extend5pOfRead1" --outReadsUnmapped "Fastx" --outSJfilterReads "Unique"). Obtained bam files were indexed with samtools index. 

Deduplication
^^^^^^^^^^^^^^
Aligned reads were deduplicated with umi_tools dedup --extract-umi-method read_id --method unique (UMI-tools version 1.1.1) 60.

Assignment of crosslink sites of CLIP reads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The deduplicated bam files of regular and trimmed chimeric eCLIP reads were converted into bed files using bedtools bamtobed (version 2.30.0) 61. The reads were the shifted by 1 nt upstream with bedtools shift -m 1 -p -1 because the UV crosslink sites should be positioned 1 nt upstream of the eCLIP read starts. For chimeric reads, the miRNA name was extracted from the read name using awk. The bed files were split into plus and minus strand, and the reads were then reduced to 1-nt crosslink events using awk.
To allow for visualization, the bed files of 1 nt events were converted to bigWig files using bedGraphToBigWig (ucsc-bedgraphtobigwig version 377, https://github.com/ucscGenomeBrowser/kent). Additionally, the bigWig files of replicates were merged by sample type (Ago-IP WT, Ago-IP KO, miR-181-enriched WT, miR-181-enriched KO) with bigWigMerge (ucsc-bigwigmerge version 377).

