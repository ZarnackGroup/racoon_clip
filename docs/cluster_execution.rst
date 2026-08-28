.. _cluster_execution:

Snakemake and Slurm execution
=============================

General Snakemake options
-------------------------

racoon_clip forwards additional, unrecognized command-line arguments to
Snakemake. These arguments can be used with both local and cluster execution.

For example, increase the time Snakemake waits for output files to appear:

.. code-block:: bash

   racoon_clip crosslinks \
       --configfile /absolute/path/to/config.yaml \
       --latency-wait 60

The same option can be used with the peak-calling workflow:

.. code-block:: bash

   racoon_clip peaks \
       --configfile /absolute/path/to/config.yaml \
       --latency-wait 60

Other useful Snakemake arguments include:

``--dry-run``
   Display the jobs that would be executed without running them.

``--keep-going``
   Continue with independent jobs after a job fails.

``--rerun-incomplete``
   Re-run jobs that previously produced incomplete output files. This option
   is enabled by default by racoon_clip.

``--latency-wait SECONDS``
   Wait for output files to become visible. This can be useful on networked
   or distributed filesystems.

For example, inspect the planned workflow without executing it:

.. code-block:: bash

   racoon_clip crosslinks \
       --configfile /absolute/path/to/config.yaml \
       --dry-run

See the
`Snakemake command-line documentation <https://snakemake.readthedocs.io/en/v7.22.0/executing/cli.html>`_
for the available options.

Slurm execution
---------------

A Snakemake profile can submit the racoon_clip workflow jobs to Slurm. The profile
keeps scheduler settings separate from the racoon_clip analysis
configuration.

Create a directory for the profile and add a file named ``config.yaml``:

.. code-block:: yaml

   cluster: >-
     mkdir -p logs/{rule} &&
     sbatch
     --cpus-per-task={threads}
     --mem={resources.mem_mb}M
     --partition={resources.partition}
     --time={resources.time}
     --job-name=smk-{rule}
     --output=logs/{rule}/{rule}-%j.out
     --error=logs/{rule}/{rule}-%j.err

   jobs: 6

   default-resources:
     - partition=your_partition
     - mem_mb=2000
     - time="48:00:00"

Replace ``your_partition`` with a valid Slurm partition on your cluster.

The profile settings have the following meanings:

``jobs``
   Maximum number of Slurm jobs submitted or running concurrently.

``threads``
   Number of CPUs requested by an individual workflow rule. The value is
   passed to Slurm as ``--cpus-per-task``.

``mem_mb``
   Default memory requested for each job, in megabytes.

``partition``
   Slurm partition to which jobs are submitted.

``time``
   Default wall-time limit for each job.

Crosslink analysis on Slurm
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   racoon_clip crosslinks \
       --configfile /absolute/path/to/config.yaml \
       --profile /absolute/path/to/slurm-profile

Peak analysis on Slurm
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   racoon_clip peaks \
       --configfile /absolute/path/to/config.yaml \
       --profile /absolute/path/to/slurm-profile

The path supplied to ``--profile`` must identify the directory containing the
profile's ``config.yaml`` file.

General Snakemake arguments can also be added to a Slurm run. For example:

.. code-block:: bash

   racoon_clip crosslinks \
       --configfile /absolute/path/to/config.yaml \
       --profile /absolute/path/to/slurm-profile \
       --latency-wait 120

Profile considerations
~~~~~~~~~~~~~~~~~~~~~~

- Ask your cluster administrators which partitions, memory limits, and wall
  times should be used.
- Keep the number of concurrent jobs appropriate for the cluster.
- Increase ``--latency-wait`` when completed files take longer to become
  visible on the cluster filesystem.
- Standard output and standard error are written below ``logs/<rule>/``.
- The racoon_clip process remains active while it submits and monitors Slurm
  jobs. Run it in a persistent shell or from a small Slurm allocation,
  according to local cluster policy.

See the
`Snakemake profile documentation <https://snakemake.readthedocs.io/en/v7.22.0/executing/cli.html#profiles>`_
and the
`smk-simple-slurm examples <https://github.com/jdblischak/smk-simple-slurm/tree/main/examples/list-partitions>`_
for additional profile options.
