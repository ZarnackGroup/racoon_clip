# racoon_clip

racoon_clip processes your iCLIP and eCLIP data from raw files to single-nucleotide crosslinks in a single step. It is an automation of the iCLIP pipeline published by Busch et al. 2020 ([iCLIP data analysis: A complete pipeline from sequencing reads to RBP binding sites](https://doi.org/10.1016/j.ymeth.2019.11.008)) making the same processing now available for both iCLIP and eCLIP data in a highly reproducible manner. 

The performed steps are an optional quality filter, optional demultiplexing, adapter trimming, genome alignment, optional deduplication and selection of single nucleotide crosslinks. For details on the performed steps please have a look at the [documentation](https://racoon-clip.readthedocs.io/en/latest/).

![](Workflow.png)


## Requirements

The following are required before installing racoon_clip

+ either conda/mamba or pip
+ python >3.9

It is recommended to install racoon_clip in a fresh conda/mamba environment. You could for example install the prerequisites with:

```
conda create -n racoon_clip pip
conda activate racoon_clip
```

or 

```
mamba create -n racoon_clip pip
mamba activate racoon_clip
``` 

## Installation

### from GitHub

Download the zip file of your preferred release from Git Hub and unzip it. Then go into the unzipped folder.

```
unzip racoon_clip-1.0.0.zip
cd racoon_clip-1.0.0
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


## Documentation and Tutorial

You can find a tutorial and all options and a details description of the performed steps at [documentation](racoon-clip.readthedocs.io).

## Citing racoon_clip

xx
