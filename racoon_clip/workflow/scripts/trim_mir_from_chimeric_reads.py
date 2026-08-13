#!/usr/bin/env python3
"""Trim canonical miRNA sequences from chimeric reads."""

import argparse
import gzip
import re
import sys

CIGAR_PATTERN = re.compile(r"(\d+)([MIDNSHP=X])")


def open_text(path, mode="rt"):
    return gzip.open(path, mode) if str(path).endswith(".gz") else open(path, mode)


def read_fasta_lengths(path):
    lengths = {}
    name = None
    length = 0
    with open_text(path) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if name is not None:
                    lengths[name] = length
                name = line[1:].split()[0]
                length = 0
            else:
                length += len(line)
    if name is not None:
        lengths[name] = length
    return lengths


def parse_int_set(value):
    return {int(item) for item in value.replace(",", " ").split()}


def cigar_operations(cigar):
    operations = [(int(length), operation) for length, operation in CIGAR_PATTERN.findall(cigar)]
    if not operations or "".join(f"{length}{operation}" for length, operation in operations) != cigar:
        raise ValueError(f"Unsupported CIGAR string: {cigar}")
    return operations


def canonical_coordinates(reference_start, cigar, reference_length, trim5):
    """Return 1-based canonical-miRNA and target-RNA starts in the original read."""
    operations = cigar_operations(cigar)
    leading_soft_clip = 0
    for length, operation in operations:
        if operation == "H":
            continue
        if operation == "S":
            leading_soft_clip = length
        break

    canonical_start = 1 + trim5 + leading_soft_clip - (reference_start - 1)
    query_indel_offset = 0
    reference_cursor = reference_start

    for length, operation in operations:
        if operation in "HPS":
            continue
        if operation == "I":
            if reference_cursor <= reference_length:
                query_indel_offset += length
            continue
        if operation in "DN":
            consumed = max(0, min(length, reference_length - reference_cursor + 1))
            query_indel_offset -= consumed
            reference_cursor += length
            continue
        if operation in "M=X":
            reference_cursor += length

    target_start = canonical_start + reference_length + query_indel_offset
    missing_5prime = max(0, 1 - canonical_start)
    inferred_start = max(1, canonical_start)
    return inferred_start, missing_5prime, target_start


def read_primary_alignments(sam_path, reference_lengths, trim5):
    alignments = {}
    with open_text(sam_path) as handle:
        for line in handle:
            if line.startswith("@"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 11:
                continue
            flag = int(fields[1])
            if flag & (0x4 | 0x10 | 0x100 | 0x800):
                continue
            read_name, reference_name = fields[0], fields[2]
            if reference_name not in reference_lengths:
                raise ValueError(f"Reference {reference_name!r} from SAM is missing from the miRNA FASTA")
            inferred_start, missing_5prime, target_start = canonical_coordinates(
                int(fields[3]), fields[5], reference_lengths[reference_name], trim5
            )
            alignments[read_name] = (
                reference_name,
                missing_5prime,
                inferred_start,
                target_start,
            )
    return alignments


def trim_fastq(fastq_path, output_path, alignments, allowed_starts, allowed_missing):
    counts = {"written": 0, "start_filtered": 0, "missing_filtered": 0, "too_short": 0}
    with open_text(fastq_path) as source, gzip.open(output_path, "wt") as output:
        while True:
            header = source.readline()
            if not header:
                break
            sequence = source.readline().rstrip("\n")
            plus = source.readline()
            quality = source.readline().rstrip("\n")
            if not quality:
                raise ValueError(f"Incomplete FASTQ record in {fastq_path}")

            read_name = header[1:].split()[0]
            alignment = alignments.get(read_name)
            if alignment is None:
                continue
            mir_name, missing_5prime, canonical_start, target_start = alignment
            if canonical_start not in allowed_starts:
                counts["start_filtered"] += 1
                continue
            if missing_5prime not in allowed_missing:
                counts["missing_filtered"] += 1
                continue

            trim_index = target_start - 1
            if trim_index < 0 or trim_index >= len(sequence):
                counts["too_short"] += 1
                continue
            original_header = header[1:].rstrip("\n")
            output.write(f"@{mir_name}_{original_header}\n")
            output.write(sequence[trim_index:] + "\n")
            output.write(plus)
            output.write(quality[trim_index:] + "\n")
            counts["written"] += 1
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sam", required=True)
    parser.add_argument("--fastq", required=True)
    parser.add_argument("--mir-fasta", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mir-starts-allowed", required=True)
    parser.add_argument("--mir-5prime-missing-allowed", required=True)
    parser.add_argument("--trim5", type=int, default=2)
    args = parser.parse_args()

    reference_lengths = read_fasta_lengths(args.mir_fasta)
    alignments = read_primary_alignments(args.sam, reference_lengths, args.trim5)
    counts = trim_fastq(
        args.fastq,
        args.output,
        alignments,
        parse_int_set(args.mir_starts_allowed),
        parse_int_set(args.mir_5prime_missing_allowed),
    )
    print(
        "Canonical miRNA trimming: "
        f"{counts['written']} reads written; "
        f"{counts['start_filtered']} excluded by mir_starts_allowed; "
        f"{counts['missing_filtered']} excluded by mir_5prime_missing_allowed; "
        f"{counts['too_short']} too short after trimming.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
