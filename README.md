# racoon_clip

<img src="Racoon_Logo_Schrift.png" width="400" alt="racoon_clip logo">

racoon_clip is a Snakemake-powered workflow that processes iCLIP, eCLIP,
seCLIP, and miR-eCLIP sequencing data to single-nucleotide crosslinks. The
``peaks`` workflow additionally calls group-level binding sites with PureCLIP.

The complete installation guide, quickstart, experiment guides, parameter
reference, and methods are available in the
[RaccoonClip documentation](https://racoon-clip.readthedocs.io/en/latest/).

## Installation

RaccoonClip currently expects Python 3.9.0, Mamba 1.x, and a compatible pip
version. Download a release archive from
[GitHub Releases](https://github.com/ZarnackGroup/racoon_clip/releases):

```bash
wget https://github.com/ZarnackGroup/racoon_clip/archive/refs/tags/[version].zip
unzip [version].zip
cd racoon_clip-[version]
```

Create and activate a dedicated environment:

```bash
conda create -n racoon_clip \
  --override-channels -c conda-forge \
  mamba=1 \
  'python_abi=*=*cp*' \
  python=3.9.0 \
  pip=25.0
conda activate racoon_clip
pip install -e .
```

Verify the installation:

```bash
racoon_clip -h
racoon_clip test --light
```

Docker and Apptainer images are also available. Container users should follow
the [bind-mount guide](https://racoon-clip.readthedocs.io/en/latest/tutorial_container.html).

## Quickstart

Use ``crosslinks`` for crosslink identification and ``peaks`` for crosslinks
followed by PureCLIP peak calling. Start from one of the tested configurations
in ``example_data`` and follow the
[quickstart](https://racoon-clip.readthedocs.io/en/latest/tutorial.html).

## Recent updates

- ``racoon_clip run`` is deprecated in favor of ``crosslinks`` and ``peaks``.
- The miR-eCLIP module now uses canonical miRNA lengths and alignment CIGAR
  information when separating miRNA and target-RNA sequence.
- miR-eCLIP peak calling combines chimeric and non-chimeric reads by
  experiment group.
- GTF annotation is optional, and an existing STAR index can be supplied.

See [Updates and migration](https://racoon-clip.readthedocs.io/en/latest/updates.html)
for details.

## Outputs

racoon_clip produces a variety of files during the different steps of the workflow that will all be stored in a folder called results. These are the main output files form the results folder:

- A summary of the performed steps called Report.html.

- The sample-wise whole aligned reads after duplicate removal in bam format. You can find them in the folder results/aligned/<sample_name>.Aligned.sortedByCoord.out.duprm.bam together with the corresponding bam.bai files.

- The group-wise whole aligned reads after duplicate removal in bam format. There will be one bam file for each group you specified in the group.txt file. If no group is specified, you get a file called all.bam where all samples are merged. They are located in the results/bam_merged/ folder.

- The sample-wise single-nucleotide crosslink files in bw format. The files are split up into the plus and minus strands. They are located at results/bw/<sample_name>sortedByCoord.out.duprm.minus.bw and results/bw/<sample_name>sortedByCoord.out.duprm.plus.bw.

- The group-wise single-nucleotide crosslink files in bw format. The files are split up into the plus and minus strands. They are located at results/bw_merged/<sample_name>sortedByCoord.out.duprm.minus.bw and results/bw_merged/<sample_name>sortedByCoord.out.duprm.plus.bw.

The output section above is intentionally retained unchanged until the
output-filename review is approved.

## Citation

- Klostermann & Zarnack 2024:
  [racoon_clip—a complete pipeline for single-nucleotide analyses of iCLIP and
  eCLIP data](https://doi.org/10.1093/bioadv/vbae084)
- Busch et al. 2020:
  [iCLIP data analysis: A complete pipeline from sequencing reads to RBP
  binding sites](https://doi.org/10.1016/j.ymeth.2019.11.008)
