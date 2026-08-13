"""Build mixed group test configurations and validate their peak outputs."""

import shutil
import tempfile
from pathlib import Path

import yaml


def create_mixed_group_config(repo_dir, base_config, output_name):
    """Create a config covering merged, singleton, and overlapping groups."""
    generated_dir = Path(tempfile.mkdtemp(prefix="racoon_clip_groups_"))
    config_path = repo_dir / base_config
    config = yaml.safe_load(config_path.read_text())
    samples = config["samples"].split()

    group_file = generated_dir / "groups.txt"
    group_file.write_text(
        f"multi {samples[0]}\n"
        f"multi {samples[1]}\n"
        f"singleton {samples[0]}\n"
    )

    config["experiment_group_file"] = str(group_file)
    config["experiment_groups"] = "multi singleton"
    config["wdir"] = f"./test/{output_name}"

    generated_config = generated_dir / config_path.name
    generated_config.write_text(yaml.safe_dump(config, sort_keys=False))
    return generated_dir, generated_config, ["multi", "singleton"]


def create_group_scenario_configs(generated_dir, mixed_config_path):
    """Create one DAG config for each supported group layout."""
    config = yaml.safe_load(mixed_config_path.read_text())
    samples = config["samples"].split()
    scenarios = {
        "no_groups": (None, ["all_samples"]),
        "multi_sample": (
            f"complete {samples[0]}\n"
            f"complete {samples[1]}\n",
            ["complete"],
        ),
        "singleton": (
            f"singleton_a {samples[0]}\n"
            f"singleton_b {samples[1]}\n",
            ["singleton_a", "singleton_b"],
        ),
        "unassigned": (
            f"partial {samples[0]}\n",
            ["partial", samples[1]],
        ),
        "overlapping": (
            f"overlap_a {samples[0]}\n"
            f"overlap_a {samples[1]}\n"
            f"overlap_b {samples[0]}\n",
            ["overlap_a", "overlap_b"],
        ),
    }

    scenario_configs = []
    for scenario, (assignments, expected_groups) in scenarios.items():
        scenario_config = dict(config)
        if assignments is None:
            scenario_config["experiment_group_file"] = ""
            scenario_config["experiment_groups"] = ""
        else:
            group_file = generated_dir / f"groups_{scenario}.txt"
            group_file.write_text(assignments)
            group_names = list(
                dict.fromkeys(
                    line.split()[0]
                    for line in assignments.splitlines()
                )
            )
            scenario_config["experiment_group_file"] = str(group_file)
            scenario_config["experiment_groups"] = " ".join(group_names)

        scenario_path = generated_dir / f"config_groups_{scenario}.yaml"
        scenario_path.write_text(yaml.safe_dump(scenario_config, sort_keys=False))
        scenario_configs.append((scenario, scenario_path, expected_groups))

    return scenario_configs


def expected_group_outputs(output_dir, groups, mir=False):
    """Return the group-level files that prove singleton and merged paths ran."""
    expected = []
    for group in groups:
        expected.extend(
            [
                output_dir / "results" / "bam_merged" / f"{group}.sort.bam",
                output_dir / "results" / "bam_merged" / f"{group}.sort.bam.bai",
                output_dir / "results" / "bw_merged" / f"{group}.plus.bw",
                output_dir / "results" / "bw_merged" / f"{group}.minus.bw",
                output_dir / "results" / "peaks" / f"pureclip_sites_{group}.bed",
                output_dir / "results" / "peaks" / f"pureclip_status_{group}.txt",
                output_dir / "results" / "peaks" / f"pureclip_{group}.log",
            ]
        )
        if mir:
            mir_dir = output_dir / "results" / "mir_analysis"
            expected.extend(
                [
                    mir_dir / "aligned_chimeric_bam_merged" / f"{group}.sort.bam",
                    (
                        mir_dir
                        / "aligned_chimeric_and_non_chimeric_bam_merged"
                        / f"{group}.sort.bam"
                    ),
                    (
                        mir_dir
                        / "aligned_chimeric_and_non_chimeric_bam_merged"
                        / f"{group}.sort.bam.bai"
                    ),
                    mir_dir / "crosslinks_merged" / f"chimeric_{group}.plus.bw",
                    mir_dir / "crosslinks_merged" / f"chimeric_{group}.minus.bw",
                    mir_dir / "peaks" / f"pureclip_sites_{group}.bed",
                    mir_dir / "peaks" / f"pureclip_status_{group}.txt",
                    mir_dir / "peaks" / f"pureclip_{group}.log",
                ]
            )
    return expected


def cleanup_generated_group_inputs(generated_dirs):
    """Remove transient group configs only after every group test succeeds."""
    for generated_dir in generated_dirs:
        shutil.rmtree(generated_dir)
