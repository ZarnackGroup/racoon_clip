#!/usr/bin/env bash
#SBATCH --job-name=get_miRBase_mir_annotation
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=01:00:00
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

set -euo pipefail

# Download and filter mature miRNA sequences from miRBase.
# Output files are written next to this script (i.e. into
# example_data/example_mir_eCLIP/), regardless of the directory this
# script is submitted/run from, so the resulting fasta sits alongside
# the example mir-eCLIP fastq files it is used with.
script_dir="/home/mek24iv/development/racoon_devel/racoon_clip/example_data/example_mir_eCLIP"

wget -O "${script_dir}/mature_mirs.fa" https://mirbase.org/download_version_files/21/mature.fa
chmod +x "${script_dir}/mature_mirs.fa"
# Keep only mouse (mmu-) entries, matching the mouse chr19 annotation
# used in the example config.
awk '/^>/{keep=($0 ~ /^>mmu-/)} keep' "${script_dir}/mature_mirs.fa" \
  > "${script_dir}/mirBase_mm10_miRNAs_mature_sequence_genes.fasta"