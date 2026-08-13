## miR module

The miR module now uses the canonical miRNA length from `mir_genome_fasta` to determine where the target-RNA part of each chimeric read begins. This replaces the previous fixed-length calculation. The alignment CIGAR string is also considered, so soft clipping, insertions, deletions, and miRNAs with different canonical lengths are handled during trimming.

`mir_starts_allowed` specifies the allowed 1-based positions at which the canonical miRNA starts within the processed read. It accounts for additional nucleotides before an otherwise complete miRNA. For example, this miRNA starts at read position 3:

```yaml
Read:       NN AACAUUCAACGCUGUCGGUGAGU TARGET
Reference:     AACAUUCAACGCUGUCGGUGAGU
```

The default is:

```yaml
mir_starts_allowed: 1 2 3 4
```

`mir_5prime_missing_allowed` specifies how many nucleotides may be missing from the canonical 5′ end of the miRNA. It is a count, so `0` means that no miRNA nucleotide is missing. In this example, the first two canonical miRNA nucleotides are missing:

```yaml
Read:            CAUUCAACGCUGUCGGUGAGU TARGET
Reference:     AACAUUCAACGCUGUCGGUGAGU
```

The default is:

```yaml
mir_5prime_missing_allowed: 0 1 2 3
```

These parameters describe independent effects: a read may contain additional nucleotides before the miRNA and also lack nucleotides from the miRNA's canonical 5′ end. After applying both, racoon-clip removes the complete canonical miRNA span and places the first target-RNA nucleotide at the beginning of the trimmed read.

The module now aligns miRNAs only in the expected forward orientation (`bowtie2 --norc`). Chimeric crosslinks are also reduced to their strand-aware 5′ nucleotide: the left edge for plus-strand alignments and the right edge for minus-strand alignments.

### Peak calling

Peak calling for miReCLIP now includes both non-chimeric and chimeric reads. For `racoon_clip peaks`, the configured experimental groups are used consistently for all merging steps:

1. Non-chimeric BAM files are merged by group using the existing BAM merge workflow. These files remain in `results/bam_merged/`.
2. Chimeric BAM files are merged using the same group definitions. The sorted group-level files are written to `results/mir_analysis/aligned_chimeric_bam_merged/`.
3. The corresponding chimeric and non-chimeric group BAMs are merged together. These combined BAMs are sorted, indexed, and written to `results/mir_analysis/aligned_chimeric_and_non_chimeric_bam_merged/`.
4. PureCLIP is run on each combined BAM. The resulting peak files are written to `results/mir_analysis/peaks/pureclip_sites_<group>.bed`.

The peak-calling section of `Report_miR.html` reports the number of PureCLIP peaks per group and displays the counts in a bar plot. This section is included only when the workflow is run with `racoon_clip peaks`.

The miR test suite now tests both modes on the miReCLIP example: it first runs `racoon_clip crosslinks` and then `racoon_clip peaks`. It can be started with:

```bash
racoon_clip test --mir --no-clean
```

