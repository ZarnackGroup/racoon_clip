Tutorial
==========

Install racoon_clip as discribed :ref:`here <installation>`. 

Get an annotation
------------------
First download a human genome assembly (as fasta) and genome annotation (as gtf).You can for examle get them from GENCODE: https://www.gencodegenes.org/human/

.. code:: bash

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
 
.. code:: bash

  head barcodes.fasta

  > >min_example_iCLIP_s1
  > NNNGGTTNN
  > >min_example_iCLIP_s2
  > NNNGGCGNN

- **groups.txt**:  A file specifying experiemnt groups. The group file has one line per sample. This line consists of first the group name and then the sample name. 

.. code:: bash

  head groups.txt
  
  > min_example_iCLIP min_example_iCLIP_s1
  > min_example_iCLIP min_example_iCLIP_s2

You can see that both samples belong to the group min_example_iCLIP. Note: This example has only one group, therfore the group.txt is not necessary. It is still shown here as an example. 

- **config_min_example_iCLIP.yaml**: The config file for racoon_clip. Inside the config file you need to adjust the path` to the sample fastq files, the adapter.fa, the barcode.fasta, the group.txt and the annotation files, so they point to the right position on your maschine.

.. Note::

  All path` need to be specified as absolut path`. Relative path` (for example starting with ~) are not allowed.

Open the config file and change the path` with your favorite editor.

.. code:: bash

  nano config_min_example_iCLIP.yaml

You should change the following lines:

.. code:: python

  wdir: "<path/where/to/put/results>"
  infiles: "<path/to/first/sample.fastq> <path/to/second/sample.fastq>"
  barcodes_fasta: "<path/to/barcodes.fasta>"
  adapter_file: "<path/to/adapter/file>"
  gtf: "<path/to/annotation.gtf>"
  genome_fasta: "<path/to/genome.fasta>"

Run the minimal example
------------------------

You can now run the minimal example:

.. code:: bash

  racoon_clip run --cores <n_cores> --configfile <path/to/config_min_example_iCLIP.yaml>

All resulting files will be writen into a folder "results" inside your wdir.


Run the minimal example from commandline, without config file
------------------------

You can also run racoon without a configfile. For the iCLIP example you would need to provide the path information as described above and  to specify the experiment_type "iCLIP" (which is already done in the example config file). 

.. code:: bash

  racoon_clip run --cores <n_cores> \
  --experiement_type "iCLIP" \
  --wdir "<path/where/to/put/results>" \
  --infiles "<path/to/first/sample.fastq> <path/to/second/sample.fastq>" \
  --barcodes_fasta "<path/to/barcodes.fasta>" \
  --adapter_file "<path/to/adapter/file>" \
  --gtf "<path/to/annotation.gtf>" \
  --genome_fasta "<path/to/genome.fasta>"

For the other minimal examples you would use "eCLIP" or "eCLIP_ENCODE" as experiemnt_type. 
 
xx change codes

.. code:: bash

  racoon_clip run --cores <n_cores> \
  --experiement_type "iCLIP" \
  --wdir "<path/where/to/put/results>" \
  --infiles "<path/to/first/sample.fastq> <path/to/second/sample.fastq>" \
  --barcodes_fasta "<path/to/barcodes.fasta>" \
  --adapter_file "<path/to/adapter/file>" \
  --gtf "<path/to/annotation.gtf>" \
  --genome_fasta "<path/to/genome.fasta>"

.. code:: bash

  racoon_clip run --cores <n_cores> \
  --experiement_type "iCLIP" \
  --wdir "<path/where/to/put/results>" \
  --infiles "<path/to/first/sample.fastq> <path/to/second/sample.fastq>" \
  --barcodes_fasta "<path/to/barcodes.fasta>" \
  --adapter_file "<path/to/adapter/file>" \
  --gtf "<path/to/annotation.gtf>" \
  --genome_fasta "<path/to/genome.fasta>"

For the multiplexed example you also need to specify --demultiplex True

.. code:: bash

  racoon_clip run --cores <n_cores> \
  --experiement_type "iCLIP" \
  --demultiplex True \
  --wdir "<path/where/to/put/results>" \
  --infiles "<path/to/first/sample.fastq> <path/to/second/sample.fastq>" \
  --barcodes_fasta "<path/to/barcodes.fasta>" \
  --adapter_file "<path/to/adapter/file>" \
  --gtf "<path/to/annotation.gtf>" \
  --genome_fasta "<path/to/genome.fasta>"

Understanding the output files
------------------------------
racoon_clip produces a variety of files during the different steps of the workflow. The files you will likely want to use downstream of racoon_clip are:

- **a summary on the perforemd steps** called Report.html.

- **the sample-wise whole aligned reads after duplicate removal in .bam format**. You can find them in the folder results/aligned/<sample_name>.Aligned.sortedByCoord.out.duprm.bam together with the corresponding .bam.bai files.

- **the group-wise whole aligned reads after duplicate removal in .bam format.** There will be one .bam file for each group you specified in the group.txt file. If no group is specified, you get a file called all.bam were all samples are merged. They are located in the results/bam_merged/ folder.

- **the sample-wise single nucleotide crosslink files in .bw format.**: The files are split up into the plus and minus strand. They are located at results/bw/<sample_name>sortedByCoord.out.duprm.minus.bw and results/bw/<sample_name>sortedByCoord.out.duprm.plus.bw.

- **the group-wise single nucleotide crosslink files in .bw format.**: The files are split up into the plus and minus strand. They are located at results/bw_merged/<sample_name>sortedByCoord.out.duprm.minus.bw and results/bw_merged/<sample_name>sortedByCoord.out.duprm.plus.bw.



Setting up and running racoon_clip on you own data
---------------------------------------------------




