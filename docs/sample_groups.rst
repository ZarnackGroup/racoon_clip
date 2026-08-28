.. _sample_groups:

Sample names and experiment groups
==================================

Sample names
------------

For non-demultiplexed inputs, racoon_clip can derive sample names from input
filenames. An explicit ``samples`` value can instead select and order the
resolved samples. Explicit names must match the input filename stems and must
be unique.

When racoon_clip performs demultiplexing, ``samples`` lists the expected
post-demultiplexing samples. Those names must also match the identifiers in
``barcodes_fasta``.

Experiment groups
-----------------

RaccoonClip produces sample-level crosslinks and group-level merged outputs.
The optional ``experiment_group_file`` assigns each sample to a group. Each
non-empty line contains a group name followed by a sample name, separated by
whitespace:

.. code-block:: text

   WT sample1
   WT sample2
   KO sample3
   KO sample4

The current workflow resolves every group present in
``experiment_group_file``. The legacy ``experiment_groups`` setting is still
accepted in configuration files, but it does not currently filter or reorder
those resolved groups. Every member in the group file must resolve to a known
sample. Samples omitted from the file are each assigned to a singleton group
named after that sample.

If no group configuration is supplied, all samples are assigned to one group
named ``all_samples``. A one-sample group is valid; its group-level files are
copied from that sample rather than passed through a multi-file merge command.

Peak calling
------------

The ``peaks`` workflow calls PureCLIP once per resolved group. Consequently,
group definitions affect both merged BAM/BigWig files and peak results. The
``crosslinks`` workflow performs the same group resolution and merging but
does not request PureCLIP peak files.

See :doc:`tutorial_output` for the documented group-level filenames after
the output-path review is complete.
