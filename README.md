# racoon_clip v 1.1.1

<img src="Racoon_Logo_Schrift.png" width="400">

racoon_clip processes your iCLIP and eCLIP data from raw files to single-nucleotide crosslinks in a single step. It is an automation of the iCLIP pipeline published by Busch et al. 2020 ([iCLIP data analysis: A complete pipeline from sequencing reads to RBP binding sites](https://doi.org/10.1016/j.ymeth.2019.11.008)) making the same processing now available for both iCLIP and eCLIP data in a highly reproducible manner. 

The performed steps are an optional quality filter, optional demultiplexing, adapter trimming, genome alignment, optional deduplication and selection of single nucleotide crosslinks. For details on the performed steps please have a look at the [documentation](https://racoon-clip.readthedocs.io/en/latest/).

![](Workflow.png)


## Requirements

The following are required before installing racoon_clip

+ mamba >= 1.3.1
+ python >= 3.9
+ *or* docker

It is recommended to install racoon_clip in a fresh conda/mamba environment. You could for example install the prerequisites with conda:

```
conda install -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*'
conda create -n racoon_clip python=3.9.0 pip
conda activate racoon_clip
```

or if you already have mamba installed:

```
mamba create -n racoon_clip python=3.9.0 pip
mamba activate racoon_clip
``` 

## Installation

### from GitHub

Download the zip file of your preferred release from Git Hub and unzip it. Then go into the unzipped folder.

```
wget https://github.com/ZarnackGroup/racoon_clip/archive/refs/tags/v1.1.1.zip
unzip racoon_clip-1.1.1.zip
cd racoon_clip-1.1.1
```

Then install racoon with pip.
```
pip install -e .

# inside a conda env, to avoid pip clashes: Find your anaconda directory, and find the actual venv folder. It should be somewhere like /anaconda/envs/venv_name/.
/anaconda/envs/venv_name/bin/pip install -e .

```

You can now check the installation by running the help option or a minimal example.

```
racoon_clip -h
```

## from Docker Image

You can also use the racoon_clip Docker Image:

```
docker pull melinak/racoon_clip
```



## Documentation and Tutorial

You can find a tutorial and all options and a details description of the performed steps in this [documentation](https://racoon-clip.readthedocs.io/en/latest/).


## Test data

You can test racoon_clip with one of the [minimal example data sets](https://github.com/ZarnackGroup/racoon_clip/tree/main/minimal_examples). See [here](https://racoon-clip.readthedocs.io/en/latest/examples.html#) for a walk-through of the examples.

racoon_clip produces a variety of files during the different steps of the workflow that will all be stored in a folder called results. These are the main output files form the results folder:

- A summary of the performed steps called Report.html.

- The sample-wise whole aligned reads after duplicate removal in bam format. You can find them in the folder results/aligned/<sample_name>.Aligned.sortedByCoord.out.duprm.bam together with the corresponding bam.bai files.

- The group-wise whole aligned reads after duplicate removal in bam format. There will be one bam file for each group you specified in the group.txt file. If no group is specified, you get a file called all.bam where all samples are merged. They are located in the results/bam_merged/ folder.

- The sample-wise single nucleotide crosslink files in bw format. The files are split up into the plus and minus strands. They are located at results/bw/<sample_name>sortedByCoord.out.duprm.minus.bw and results/bw/<sample_name>sortedByCoord.out.duprm.plus.bw.

- The group-wise single nucleotide crosslink files in bw format. The files are split up into the plus and minus strands. They are located at results/bw_merged/<sample_name>sortedByCoord.out.duprm.minus.bw and results/bw_merged/<sample_name>sortedByCoord.out.duprm.plus.bw.




## Citing racoon_clip

We are currently working on the racoon_clip manuscript.
