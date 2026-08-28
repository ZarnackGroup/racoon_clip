.. _cluster_execution:

Slurm and cluster execution
===========================

RaccoonClip forwards additional Snakemake arguments, including profile
options. A Slurm profile keeps scheduler settings separate from the analysis
configuration.

The following existing command examples are retained unchanged pending the
command-example review:

.. code-block:: bash

   racoon_clip crosslinks \
     --configfile <your_configfile.yaml> \
     -p \
     --cores 10 \
     --profile <path/to/your/slurm/profile> \
     --wait-for-files \
     --latency-wait 60

.. code-block:: bash

   racoon_clip peaks \
     --configfile <your_configfile.yaml> \
     -p \
     --cores 10 \
     --profile <path/to/your/slurm/profile> \
     --wait-for-files \
     --latency-wait 60

The existing profile example is also retained unchanged pending that review:

.. code-block:: yaml

   cluster:
   mkdir -p logs/{rule} &&
   sbatch
   --cpus-per-task={threads}
   --mem={resources.mem_mb}
   --partition={resources.partition}
   --job-name=smk-{rule}-{wildcards}
   --output=logs/{rule}/{rule}-{wildcards}-%j.out
   default-resources:
   - partition=<your_partitions>
   - mem_mb=2000
   - time="48:00:00"
   jobs: 6

Profile considerations
----------------------

- Match each rule's requested threads to ``--cpus-per-task``.
- Keep logs in a rule- and job-specific directory.
- Set memory and wall time through Snakemake resources rather than applying
  one unusually large allocation to every rule.
- Increase ``--latency-wait`` on filesystems where completed job outputs
  become visible slowly.
- Use a bounded number of concurrent jobs appropriate for the cluster.

See the
`Snakemake profile documentation <https://snakemake.readthedocs.io/en/stable/executing/cli.html#profiles>`_
and the
`smk-simple-slurm examples <https://github.com/jdblischak/smk-simple-slurm/tree/main/examples/list-partitions>`_.
