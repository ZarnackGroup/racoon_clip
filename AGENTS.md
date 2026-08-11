# AGENTS.md — RaccoonClip Development

## Project

This repository contains **RaccoonClip**, a command-line tool for running a Snakemake-based CLIP-seq analysis pipeline.

Development commonly involves:

* Python
* Snakemake
* Bash
* Conda/Mamba environments
* Bioinformatics command-line tools
* SLURM-based HPC execution

Prefer small, targeted changes that preserve the existing architecture and behavior.

## Workspace and File Access

Work only within the current project/workspace unless explicitly instructed otherwise.

Paths outside the workspace may be referenced in scripts or configuration files, but do not inspect, read, modify, enumerate, or search files outside the workspace unless explicitly authorized.

Do not inspect sequencing or other potentially large/raw data files unless explicitly requested.

Do not read:

* `*.fastq`
* `*.fastq.gz`
* `*.fq`
* `*.fq.gz`
* `*.bam`
* `*.sam`
* `*.cram`
* `*.sra`

Paths to these files may be used as opaque strings when required for scripts or configuration.

Do not recursively inspect large data directories merely because they are referenced by the workflow.

## Editing Files

Reading and editing source-code files inside this repository is allowed without asking for confirmation.

This includes:

* Python
* Snakemake/Snakefiles
* Bash
* YAML configuration
* test files
* small text/configuration files

Prefer editing existing files over creating unnecessary new files.

Keep changes focused on the requested task.

Do not perform unrelated refactoring unless necessary for the requested change.

## Deleting Files

**Always ask before deleting any file or directory.**

This applies even when the file appears obsolete, generated, temporary, or redundant.

Do not use destructive commands such as:

```bash
rm
rm -r
rm -rf
git clean
```

without explicit approval.

## Documentation

Do **not** modify project documentation automatically.

This includes:

* `README*`
* documentation directories
* user-facing installation instructions
* tutorials
* example documentation

If a code change means documentation should probably be updated, report:

1. which documentation should be updated;
2. what information is now outdated;
3. what change is recommended.

Leave the actual documentation edit to the user unless explicitly instructed to modify it.

## Conda and Mamba Environments

Do **not** modify Conda/Mamba environment definitions without explicit approval.

This includes:

* adding packages;
* removing packages;
* changing package versions;
* changing channels;
* changing channel priority;
* regenerating environment files;
* updating lock files.

Environment YAML files should be treated as compatibility-sensitive parts of RaccoonClip.

If an environment change appears necessary, explain:

* which environment is affected;
* what dependency needs changing;
* why;
* what version/channel change is recommended.

Then wait for approval.

Do not silently upgrade packages to solve dependency conflicts.

## Snakemake

Preserve the existing Snakemake workflow structure and conventions.

When adding or changing rules:

* inspect related rules first;
* follow existing naming conventions;
* preserve input/output relationships;
* avoid unnecessary duplication;
* use existing configuration mechanisms where possible;
* ensure dependencies between rules remain explicit.

After meaningful Snakemake changes, perform appropriate validation.

At minimum, where applicable:

```bash
snakemake --dry-run
```

and check DAG construction:

```bash
snakemake --dag
```

The DAG check should verify that the rules still connect correctly and that the workflow can be constructed.

Do not launch large or computationally expensive workflow runs automatically.

Small test/example workflows may be run when appropriate.

## Bash and SLURM

Shell scripts intended to run computational jobs on the cluster should contain a SLURM `sbatch` header.

Default header:

```bash
#!/usr/bin/env bash
#SBATCH --job-name=job
#SBATCH --cpus-per-task=4
#SBATCH --mem=10G
#SBATCH --time=24:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

set -euo pipefail
```

Adjust the job name and resources when the task clearly requires different values.

### CPU usage

Use:

```bash
#SBATCH --cpus-per-task=4
```

when the program or workflow can actually make use of parallel execution.

If the commands in the script are not parallelized, request only:

```bash
#SBATCH --cpus-per-task=1
```

Do not request additional CPUs when they will not be used.

When a program accepts a thread/CPU argument, connect it to the allocated SLURM CPUs where appropriate.

Prefer:

```bash
${SLURM_CPUS_PER_TASK}
```

rather than independently hard-coding the number of threads.

## Bash Style

Use:

```bash
set -euo pipefail
```

for newly written Bash scripts unless there is a specific reason not to.

Quote variables:

```bash
"$file"
"$directory"
```

Prefer readable multi-line commands for commands with many arguments.

Use meaningful variable names.

Avoid unnecessary subshells, pipes, and temporary files.

Check that paths and output directories exist where appropriate.

## Comments

Use a **moderately talkative commenting style**.

Comments should explain:

* non-obvious logic;
* why a particular approach is used;
* important assumptions;
* unusual bioinformatics/tool behavior;
* workflow dependencies that are not obvious from the code.

Do not comment every line.

As a rough guideline, aim for approximately **one useful comment per five lines of non-trivial code**, but prioritize clarity rather than enforcing an exact ratio.

Avoid comments that merely restate the code.

Prefer:

```python
# Keep multimappers because downstream filtering uses alignment scores.
reads = load_alignments(path)
```

over:

```python
# Load alignments.
reads = load_alignments(path)
```

## Python

Follow the existing project style.

Prefer:

* small functions;
* descriptive names;
* explicit error handling;
* standard-library solutions when reasonable;
* minimal new dependencies;
* clear separation of workflow logic and command-line interfaces.

Do not introduce new dependencies without a clear need.

If a new dependency would require changing a Conda environment, ask first.

## Testing

Run the smallest relevant tests after making changes.

Prefer targeted tests first.

For Python changes, run the relevant unit tests if available.

For Snakemake changes, use dry-run and DAG validation where appropriate.

For Bash changes, syntax-check scripts when possible:

```bash
bash -n script.sh
```

Do not run large datasets or expensive cluster jobs merely to test a small code change.

If full validation requires cluster resources or real data, explain what should be run rather than launching it automatically.

## Raw and Large Data

Do not inspect raw sequencing data.

Do not use commands such as:

```bash
cat
head
tail
less
zcat
samtools view
```

on FASTQ/BAM/SAM/CRAM/SRA files unless explicitly instructed.

Do not recursively search raw-data directories.

When a script needs a raw-data path, treat the path as an opaque input.

Prefer tiny synthetic/example data for development tests.

## Git

First determine whether the files being modified belong to an existing Git repository.

Use:

```bash
git rev-parse --show-toplevel
```

when needed.

The current workspace directory is **not necessarily the Git repository root**.

If an existing Git repository contains the files being modified, perform Git operations from that repository.

If there is no Git repository:

* do not initialize one;
* do not run `git init`;
* do not create Git metadata.

## Git Commits

Git commits are allowed.

For meaningful completed changes, create a checkpoint commit when the repository is in a sensible state.

Do **not** commit merely because a fixed amount of time has passed.

Prefer commits at logical checkpoints such as:

* completing a feature;
* fixing a bug;
* completing a meaningful refactor;
* getting a previously failing test to pass;
* completing a coherent Snakemake rule change.

Before committing:

```bash
git status
git diff
```

Review what will be committed and avoid including unrelated files.

Commit messages created by Codex should begin with:

```text
codex:
```

For example:

```text
codex: simplify example sequence extraction
```

or:

```text
codex: add Snakemake rule for polyA analysis
```

Keep commits focused and reversible.

Do not amend, squash, rebase, reset, or rewrite existing Git history unless explicitly instructed.

## Git Push

**Never run `git push`.**

Do not push branches, tags, or commits to any remote.

The user will perform all pushes manually.

Do not change Git remotes or authentication configuration.

## Safety Before Large Changes

Before making a broad or potentially disruptive change:

1. inspect the relevant existing implementation;
2. inspect Git status;
3. understand which files are affected;
4. prefer the smallest viable change;
5. preserve existing behavior unless the task explicitly requires changing it.

If multiple approaches are possible and one would substantially change the architecture, explain the options before performing the larger redesign.

## Generated and Temporary Files

Avoid committing:

* temporary files;
* logs;
* large generated outputs;
* `.snakemake` working files;
* test outputs;
* raw sequencing data;
* editor-specific temporary files.

Do not delete such files without approval if they already exist.

## Error Handling

Do not hide errors merely to make commands succeed.

Avoid patterns such as:

```bash
command || true
```

unless failure is genuinely expected and intentionally handled.

When a command fails:

1. inspect the actual error;
2. identify the likely cause;
3. make the smallest appropriate correction;
4. rerun the relevant test.

Do not repeatedly retry the same failing operation without changing anything.

## Dependencies and Compatibility

RaccoonClip has compatibility constraints involving older versions of Python, Mamba, Snakemake, Conda packages, and bioinformatics tools.

Treat existing version pins as intentional unless evidence shows otherwise.

Do not automatically modernize dependencies.

Do not change Python, Mamba, Snakemake, or Conda package versions simply because newer versions exist.

Compatibility and reproducibility take priority over modernization.

## General Development Principle

Prefer:

**understand → make a small change → test → inspect diff → commit**

over large speculative changes.

Preserve reproducibility of the RaccoonClip workflow and avoid modifying data, environments, documentation, or repository history unless the requested development task requires it.
