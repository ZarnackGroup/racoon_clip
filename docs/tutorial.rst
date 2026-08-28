.. _tutorial:

Quickstart
==========

This page shows the shortest route from an installed package to a first
analysis. For explanations of experiment types and optional processing
stages, continue with :doc:`tutorial_customise`.

Choose the workflow
-------------------

Use ``crosslinks`` when the required result is a set of single-nucleotide
crosslink tracks. Use ``peaks`` when PureCLIP peak calling should
run after crosslink identification.

.. code:: bash

   racoon_clip crosslinks --configfile <your_configfile.yaml> --cores <n_cores> [OPTIONS]
   racoon_clip peaks --configfile <your_configfile.yaml> --cores <n_cores> [OPTIONS]

Prepare a minimal configuration
-------------------------------

Create a YAML file containing the input reads, reference genome, and one
supported experiment type. Relative paths are resolved from the directory
where ``racoon_clip`` is started.

.. code-block:: yaml

   wdir: ./racoon_clip_out
   infiles: "reads/sample1.fastq.gz reads/sample2.fastq.gz"

   experiment_type: iCLIP2

   genome_fasta: references/genome.fa
   gtf: references/annotation.gtf
   read_length: 75

   # Optional for the peaks workflow
   morePureclipParameters: "-iv 'chr1;chr2;chr3;'"

** Notes:**

- When demultiplexing, provide one multiplexed input file together with ``samples`` and ``barcodes_fasta``. When not demultiplexing, racoon_clip can infer each sample name from its FASTQ filename by removing the ``.fastq``, ``.fq``, ``.fastq.gz``, or ``.fq.gz`` suffix. 

- **Use absolute paths** for input files, reference files, auxiliary files, and the output directory. Relative paths are unsupported and may fail during execution. Paths beginning with ``~`` are not expanded.

- Choose exactly one supported ``experiment_type`` from :doc:`tutorial_customise`. 


Run and inspect
---------------

Run one of the commands above from the repository or analysis directory.
racoon_clip writes a merged ``*_updated.yaml`` configuration next to the
provided configuration file. Keep this file with the results because it
records the defaults, file settings, and command-line overrides used for the
run.

See :doc:`tutorial_output` for result interpretation and
:doc:`troubleshooting` for common startup errors.
