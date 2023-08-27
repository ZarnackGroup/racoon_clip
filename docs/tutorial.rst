Tutorial
==========

Install racoon_clip as discribed :ref:`here <installation>`. 

Get an annotation
------------------
First download a human genome assembly (as fasta) and genome annotation (as gtf).You can for examle get them from GENCODE: https://www.gencodegenes.org/human/

.. code:: console

  mkdir annotation
  cd annotation
  wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/GRCh38.p14.genome.fa.gz
  wget https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gtf.gz
  gunzip *


Set up one of the minimal examples
-----------------------------------
Now you can run an example provided with racoon_clip.  Go into the folder minimal examples and unzip te example, that you want to test. There are 4 examples, one for iCLIP, one for eCLIP, one for eCLIP downloaded from encode and one for a multiplexed iCLIP (where racoon needs to perform demultiplexing). In this tutorial the iCLIP data set is show exemplarily, but you can run this tutorial with each of these examples.

.. code:: bash

  cd minimal_examples
  unzip minimal_example_iCLIP.zip


Go into the folder of the example and unzip all files.

.. code:: bash

  cd minimal_examples/minimal_example_iCLIP
  gunzip *
  ls

You should now see the following files in the folder:

- **min_example_iCLIP_s1.fastq, min_example_iCLIP_s2.fastq**: Two samples with raw reads of an iCLIP experiment.

- **adapter.fa**: A fasta file containing the adapters used in the experiment. These will be trimmed off.

- **barcodes.fasta**: A fasta file containing the barcodes containing the experimental barcode and the UMI of each sample.
 
.. code: console

  head barcodes

  > >min_example_iCLIP_s1
  > NNNGGTTNN
  > >min_example_iCLIP_s2
  > NNNGGCGNN

- **groups.txt**:  

- **config_min_example_iCLIP.yaml**: The config file for racoon_clip. Inside the config file you need to change the directories to the sample fastq files

Run the minimal example
------------------------



Setting up and running racoon_clip on you own data
---------------------------------------------------




