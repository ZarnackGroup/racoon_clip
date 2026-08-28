.. _troubleshooting:

Troubleshooting
===============

Installation and Mamba
----------------------

``libmamba`` or solver errors
   Confirm that the racoon_clip environment contains Mamba 1.x. A newer
   system Mamba does not replace the version required inside this environment.

``racoon_clip: command not found``
   Activate the environment used for installation and confirm that ``pip``
   installed into that same environment.

Configuration errors
--------------------

Unknown parameter
   Configuration keys are case-sensitive. Use the exact configuration name;
   for example, ``infiles`` rather than ``infile``. The error message may
   suggest the closest supported key.

Unknown ``experiment_type``
   Use one of the values listed in :doc:`tutorial_customise`. Values are
   matched case-insensitively, but punctuation and spelling must otherwise
   agree.

Sample has no matching input
   Explicit sample names must match the input filename without its recognized
   sequencing-file suffix. Also check for duplicate basenames in different
   directories.

Demultiplexing resolves multiple inputs
   Demultiplexing expects one multiplexed input. Supply the post-demultiplexing
   sample names and a matching ``barcodes_fasta``.

Reference and alignment errors
------------------------------

Missing reference
   Confirm that ``genome_fasta``, an optional ``gtf``, and any supplied
   ``star_index`` are readable from the environment where Snakemake jobs run.

Invalid STAR index
   A supplied ``star_index`` must be a directory containing STAR's ``Genome``,
   ``SA``, and ``SAindex`` files.

Cluster jobs start but outputs are not detected
   Increase Snakemake's latency wait and confirm that compute nodes see the
   same paths as the submission host.

Peak calling
------------

PureCLIP uses substantial memory
   Restrict model training to representative chromosomes with
   ``morePureclipParameters`` and request suitable memory through the
   Snakemake profile.

Container cannot see input or output
   Bind every host directory referenced by the configuration into the
   container and use the corresponding in-container paths. See
   :doc:`tutorial_container`.

Testing a problem
-----------------

Start with ``racoon_clip test --light`` to check configuration and DAG
construction. Focused modes such as ``--mir``, ``--groups``, and
``--fastqscreen`` can narrow failures. Add ``--no-clean`` when generated
files are needed for inspection.

