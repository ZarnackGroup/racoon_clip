.. _updates:

Updates and migration
=====================

Deprecated ``run`` command
--------------------------

The ``run`` command is deprecated and retained only for backward
compatibility. It prints a warning and executes the same crosslink workflow
as ``crosslinks``.

Existing scripts should migrate as follows:

.. code-block:: bash

   # Old command
   racoon_clip run --configfile my_config.yaml --cores <n>

   # Crosslink identification
   racoon_clip crosslinks --configfile my_config.yaml --cores <n>

   # Crosslinks followed by peak calling
   racoon_clip peaks --configfile my_config.yaml --cores <n>

The command examples above are copied from the previous migration guide and
remain unchanged pending the command-example review.

Recent miR-eCLIP changes
------------------------

The miR module now determines the target-RNA boundary from each canonical
miRNA sequence and the alignment CIGAR rather than assuming one fixed miRNA
length. ``mir_starts_allowed`` controls accepted canonical start positions,
while ``mir_5prime_missing_allowed`` independently controls accepted missing
bases at the canonical 5-prime end.

The module aligns miRNAs in the expected forward orientation. For the
``peaks`` workflow, chimeric and non-chimeric group BAMs are combined before
PureCLIP peak calling.

The detailed paths remain in ``MIR_MODULE_UPDATE.md`` until the separate
output-filename review is approved.

