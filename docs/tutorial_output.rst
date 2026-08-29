.. _tutorial_output:

Understanding the output files
==============================

.. contents:: 
    :depth: 2

racoon_clip produces a variety of files during the different steps of the workflow. The files you will likely want to use downstream of racoon_clip are:

racoon_clip crosslink produces:
-------------------------

- **a summary of the performed steps** called Report.html.

- **The sample-wise whole aligned reads after duplicate removal in BAM format**. You can find them in the folder results/aligned/<sample_name>.Aligned.sortedByCoord.out.duprm.bam together with the corresponding bam.bai files.

- **The group-wise whole aligned reads after duplicate removal in BAM format.** There will be one bam file for each group you specified in the group.txt file. If no group is specified, you get a file called all.bam where all samples are merged. They are located in the results/bam_merged/ folder.

- **The sample-wise single nucleotide crosslink files in bw format.**: The files are split up into the plus and minus strands. They are located at results/bw/<sample_name>sortedByCoord.out.duprm.minus.bw and results/bw/<sample_name>sortedByCoord.out.duprm.plus.bw.

- **The group-wise single nucleotide crosslink files in bw format.**: The files are split up into the plus and minus strands. They are located at results/bw_merged/<sample_name>sortedByCoord.out.duprm.<strand>.bw.


racoon_clip peaks additionally produces:
------------------------

- all of the files above
- the called binding peaks in BED format. Peak calling is performed on the merged groups. The peaks are located at results/peaks/<group_name>.bed


the experiment_type miR-eCLIP additionally produces:
------------------------------

