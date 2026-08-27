"""Resolve user-provided FASTQ inputs and map them to sample names."""

import glob
import os
import shlex


FASTQ_EXTENSIONS = (".fastq.gz", ".fq.gz", ".fastq", ".fq")


def resolve_infiles(infiles, demultiplex=False):
    """Expand every input token and return validated FASTQ paths."""
    if not isinstance(infiles, str):
        raise ValueError("'infiles' must be a string containing FASTQ paths or glob patterns.")

    tokens = shlex.split(infiles)
    if not tokens:
        raise ValueError("'infiles' is empty. Provide at least one FASTQ file or glob pattern.")

    resolved = []
    unmatched_patterns = []
    for token in tokens:
        if glob.has_magic(token):
            matches = sorted(glob.glob(token))
            if not matches:
                unmatched_patterns.append(token)
            resolved.extend(matches)
        else:
            resolved.append(token)

    if unmatched_patterns:
        raise ValueError(
            "No files found matching input pattern(s): "
            + ", ".join(unmatched_patterns)
        )

    # A file can be selected by overlapping patterns; process it only once.
    unique_paths = []
    seen_paths = set()
    for path in resolved:
        identity = os.path.abspath(path)
        if identity not in seen_paths:
            unique_paths.append(path)
            seen_paths.add(identity)

    missing = [path for path in unique_paths if not os.path.isfile(path)]
    if missing:
        raise ValueError("Input FASTQ file(s) do not exist: " + ", ".join(missing))

    unreadable = [path for path in unique_paths if not os.access(path, os.R_OK)]
    if unreadable:
        raise ValueError("Input FASTQ file(s) are not readable: " + ", ".join(unreadable))

    invalid_extensions = [
        path for path in unique_paths if not path.lower().endswith(FASTQ_EXTENSIONS)
    ]
    if invalid_extensions:
        raise ValueError(
            "Input files must end in .fastq, .fq, .fastq.gz, or .fq.gz: "
            + ", ".join(invalid_extensions)
        )

    if demultiplex and len(unique_paths) != 1:
        raise ValueError(
            "demultiplex=True requires exactly one input FASTQ file, but "
            f"{len(unique_paths)} files were resolved."
        )

    return unique_paths


def sample_name_from_fastq(path):
    """Return a sample name from a supported FASTQ filename."""
    basename = os.path.basename(path)
    for extension in FASTQ_EXTENSIONS:
        if basename.lower().endswith(extension):
            return basename[: -len(extension)]
    raise ValueError(f"Cannot derive a sample name from unsupported FASTQ path: {path}")


def build_sample_file_map(input_files, configured_samples=None):
    """Return validated sample names and their exact input file paths."""
    name_to_file = {}
    for path in input_files:
        sample = sample_name_from_fastq(path)
        if sample in name_to_file:
            raise ValueError(
                f"Multiple input files resolve to sample name '{sample}': "
                f"{name_to_file[sample]}, {path}"
            )
        name_to_file[sample] = path

    samples = configured_samples.split() if configured_samples else list(name_to_file)
    if len(samples) != len(set(samples)):
        raise ValueError("Sample names must be unique.")

    missing = [sample for sample in samples if sample not in name_to_file]
    if missing:
        raise ValueError(
            "The following configured sample names have no matching input file: "
            + ", ".join(missing)
            + f". Available names: {sorted(name_to_file)}"
        )

    return samples, {sample: name_to_file[sample] for sample in samples}
