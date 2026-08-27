#!/usr/bin/env python3
"""Prepare a DNA5 genome FASTA for PureCLIP."""

import argparse
import os
import tempfile
from pathlib import Path


DNA5 = frozenset("ACGTNacgtn")
URACIL = frozenset("Uu")


def scan_symbols(fasta_path):
    """Return extended symbols and whether uracil occurs on FASTA sequence lines."""
    symbols = set()
    has_uracil = False
    with open(fasta_path, encoding="ascii") as fasta:
        for line in fasta:
            if line.startswith(">"):
                continue
            sequence = line.strip()
            has_uracil = has_uracil or any(base in URACIL for base in sequence)
            symbols.update(
                base for base in sequence if base not in DNA5 and base not in URACIL
            )
    return symbols, has_uracil


def write_compatible_fasta(source_path, output_path):
    """Write DNA5 FASTA, changing U/u to T/t and other unsupported symbols to N."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.", dir=output_path.parent, text=True
    )
    try:
        with open(source_path, encoding="ascii") as source, os.fdopen(
            descriptor, "w", encoding="ascii"
        ) as output:
            for line in source:
                if line.startswith(">"):
                    output.write(line)
                    continue
                output.write(
                    "".join(
                        "T"
                        if base == "U"
                        else "t"
                        if base == "u"
                        else base
                        if base in DNA5 or base in "\r\n"
                        else "N"
                        for base in line
                    )
                )
        os.replace(temporary_name, output_path)
    except Exception:
        if os.path.exists(temporary_name):
            os.remove(temporary_name)
        raise


def write_status(status_path, genome_path, symbols, has_uracil):
    status_path = Path(status_path)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(
        f"GenomePath\t{genome_path}\n"
        f"ExtendedIupacToN\t{str(bool(symbols)).lower()}\n"
        f"UracilToT\t{str(has_uracil).lower()}\n"
        f"ExtendedSymbols\t{','.join(sorted(symbols))}\n"
    )


def prepare_pureclip_genome(
    source_path, preferred_output_path, fallback_output_path, status_path
):
    """Select or create a PureCLIP-compatible FASTA and record the selected path."""
    source_path = Path(source_path).resolve()
    preferred_output_path = Path(preferred_output_path).resolve()
    fallback_output_path = Path(fallback_output_path).resolve()
    symbols, has_uracil = scan_symbols(source_path)

    if not symbols and not has_uracil:
        selected_path = source_path
        print("No FASTA alphabet changes needed; PureCLIP will use the original genome.")
    elif preferred_output_path.exists():
        selected_path = preferred_output_path
        print(f"Reusing existing PureCLIP-compatible FASTA: {selected_path}")
    else:
        selected_path = (
            preferred_output_path
            if os.access(preferred_output_path.parent, os.W_OK)
            else fallback_output_path
        )
        try:
            write_compatible_fasta(source_path, selected_path)
        except PermissionError:
            if selected_path == fallback_output_path:
                raise
            selected_path = fallback_output_path
            write_compatible_fasta(source_path, selected_path)
        print(f"Wrote PureCLIP-compatible FASTA: {selected_path}")

    if symbols:
        printable_symbols = ", ".join(repr(symbol) for symbol in sorted(symbols))
        print(
            f"Replaced extended IUPAC symbols with N for PureCLIP: {printable_symbols}"
        )
    if has_uracil:
        print("Replaced U/u with T/t in the genome FASTA for PureCLIP compatibility.")

    write_status(status_path, selected_path, symbols, has_uracil)
    return selected_path, symbols, has_uracil


def main():
    parser = argparse.ArgumentParser(
        description="Prepare an A/C/G/T/N genome FASTA for PureCLIP."
    )
    parser.add_argument("--input", required=True, help="Original genome FASTA")
    parser.add_argument(
        "--preferred-output",
        required=True,
        help="Compatible FASTA beside the original genome",
    )
    parser.add_argument(
        "--fallback-output",
        required=True,
        help="Compatible FASTA in the workflow temporary directory",
    )
    parser.add_argument("--status", required=True, help="Compatibility status file")
    args = parser.parse_args()
    prepare_pureclip_genome(
        args.input, args.preferred_output, args.fallback_output, args.status
    )


if __name__ == "__main__":
    main()
