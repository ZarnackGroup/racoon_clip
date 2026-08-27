"""Helpers for STAR runs with optional transcript annotations."""

import re
import shlex


def generated_star_index_paths(gtf, genome_fasta):
    """Return generated STAR index and checkpoint paths."""
    reference = gtf or genome_fasta
    if not reference:
        raise ValueError("A genome FASTA is required to generate a STAR index.")
    base = re.sub(r"\.[^.]+$", "", str(reference))
    return base + "_idx/", base + "_idx.chpnt"


def star_annotation_arguments(gtf, sjdb_overhang):
    """Return annotation-specific STAR arguments, or nothing without a GTF."""
    if not gtf:
        return ""
    return (
        f"--sjdbGTFfile {shlex.quote(str(gtf))} "
        f"--sjdbOverhang {int(sjdb_overhang)}"
    )
