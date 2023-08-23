# racoon-clip

racoon_clip processes your iCLIP and eCLIP data from raw files to single-nucleotide crosslinks in a single step. It is an automatition of the iCLIP pipeline pubished by Busch et al. 2020 ([iCLIP data analysis: A complete pipeline from sequencing reads to RBP binding sites](https://doi.org/10.1016/j.ymeth.2019.11.008)) making the same processing now availabe for both iCLIP and eCLIP data in a highly reproducible manner. 

The performed steps are an optional quality filter, optional demultiplaexing, adapter trimming, genome alignment, optional deduplication and selection of single nucleotide crosslinks. For details on the performed steps please have a look at the readthedocsxx.

![](Workflow.png)


## Requirements

The following are required before installing racoon_clip

+ pip
+ python >3.9
+ mamba

It is recommended to install racoon_clip it a fresh conda/mamba enviroment. You could for example install the prequisites with:

```
conda create -n racoon_clip pip
conda activate racoon_clip
conda install -c conda-forge mamba
```

or 

```
mamba create -n racoon_clip pip
mamba activate racoon_clip
``` 

## Installation

### from GitHub

Download the zip file of your prefered release from github and unzip it. Then go into the unziped folder.

```
unzip racoon_clip-1.0.0.zip
cd racoon_clip-1.0.0
```

Then install racoon with pip.
```
pip install --user -e .
```

You can now check the installation by running help option or a minimal example.

```
racoon_clip -h
```


## Documanetation and Tutorial

You can find a tutarial and all options and a details description of the performed steps at xxreadthedocs.

## Citing racoon_clip

xx
