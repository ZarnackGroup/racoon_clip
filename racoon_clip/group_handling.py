"""Resolve experimental groups consistently across racoon-clip workflows."""

from collections import OrderedDict
from pathlib import Path


def resolve_groups(samples, group_file=None):
    """Return an ordered mapping of output group names to sample names."""
    samples = list(samples)
    if len(samples) != len(set(samples)):
        raise ValueError("Sample names must be unique.")

    if not group_file:
        return OrderedDict([("all_samples", samples)])

    group_path = Path(group_file)
    if not group_path.is_file():
        raise FileNotFoundError(f"Experiment group file not found: {group_path}")

    groups = OrderedDict()
    known_samples = set(samples)
    for line_number, raw_line in enumerate(group_path.read_text().splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        columns = line.split()
        if len(columns) != 2:
            raise ValueError(
                f"Invalid experiment group line {line_number}: expected "
                "'<group> <sample>'."
            )

        group, sample = columns
        if "/" in group or "\\" in group:
            raise ValueError(
                f"Invalid group name '{group}': path separators are not allowed."
            )
        if sample not in known_samples:
            raise ValueError(
                f"Unknown sample '{sample}' in experiment group file."
            )

        members = groups.setdefault(group, [])
        if sample not in members:
            members.append(sample)

    if not groups:
        raise ValueError("The experiment group file contains no group assignments.")

    assigned_samples = {
        sample for members in groups.values() for sample in members
    }
    for sample in samples:
        if sample in assigned_samples:
            continue
        if sample in groups:
            raise ValueError(
                f"Cannot create a singleton group for unassigned sample '{sample}' "
                "because that name is already used by another group."
            )
        groups[sample] = [sample]

    return groups
