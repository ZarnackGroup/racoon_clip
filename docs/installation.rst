Installation
=========================



RECOMMENDED: use Docker Image
---------------------

If your system has Docker, Singularity or Apptainer installed, it is recommended to use the racoon_clip Docker Image:

.. code:: bash

   docker pull melinak/racoon_clip:latest
   or
   apptainer pull racoon_clip.sif docker://melinak/racoon_clip:latest
   or
   singularity pull racoon_clip.sif docker://melinak/racoon_clip:latest



Install from GitHub
---------------------

Download the zip file of your preferred release from GitHub and unzip it. Then go into the unzipped folder.

.. code:: bash

   wget https://github.com/ZarnackGroup/racoon_clip/archive/refs/tags/[version].zip
   unzip [version].zip
   cd racoon_clip-[version]



It is recommended to install racoon_clip in a fresh conda/mamba environment. You could for example install the prerequisites with conda:

.. code:: bash

   conda install -n base --override-channels -c conda-forge mamba 'python_abi=*=*cp*'
   conda create -n racoon_clip python=3.9.0 pip
   conda activate racoon_clip


or if you already have mamba installed:

.. code:: bash

   mamba create -n racoon_clip python=3.9.0 pip
   mamba activate racoon_clip


Then install racoon with pip.

.. code:: bash

   pip install -e .

   # Inside a conda environment, do the following to avoid pip clashes: 
   # Find your anaconda directory and the folder of the environment. 
   # (It should be somewhere like /anaconda/envs/racoon_clip/.)

   /anaconda/envs/racoon_clip/bin/pip install -e .

You can now check the installation by running the help option and then :ref:`quickstart <tutorial>` your analysis.

.. code:: bash

   racoon_clip -h

Check Installation with Tests
-----------------------------

racoon_clip provides built-in test commands to verify your installation:

**Light Test (Quick verification):**

.. code:: bash

   racoon_clip test light

This runs a quick test doing basic functionality checks

**Full Test (Comprehensive verification):**

.. code:: bash

   racoon_clip test full

This runs the complete test suite including:
- All tests from the light test
- Full workflow execution tests with example data





