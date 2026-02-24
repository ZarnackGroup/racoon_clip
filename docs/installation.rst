Installation
=========================



Install from GitHub
---------------------

Download the zip file of your preferred release from GitHub and unzip it. Then go into the unzipped folder.
You can get the link to the zip file of the newest version from `the GitHub release page <https://github.com/ZarnackGroup/racoon_clip/releases>`_. 

.. code:: bash

   wget https://github.com/ZarnackGroup/racoon_clip/archive/refs/tags/[version].zip
   unzip [version].zip
   cd racoon_clip-[version]



It is recommended to install racoon_clip in a fresh conda/mamba environment. You could for example install the prerequisites with conda:

.. code:: bash
  
   conda create -n racoon_clip \
  --override-channels -c conda-forge \
  mamba=1 \
  'python_abi=*=*cp*' \
  python=3.9.0 \
  pip=25.0
   conda activate racoon_clip


or if you already have mamba installed:

.. code:: bash

   mamba create -n racoon_clip python=3.9.0 pip=25.0
   mamba activate racoon_clip


Then install racoon with pip.

.. code:: bash

   pip install -e .

   # Inside a conda environment, do the following to avoid pip clashes: 
   # Find your anaconda directory and the folder of the environment. 
   # (It should be somewhere like /anaconda/envs/racoon_clip/.)

   /anaconda/envs/racoon_clip/bin/pip install -e .



Check Installation with Tests
-----------------------------
You can now check the installation by running the help option and then :ref:`quickstart <tutorial>` your analysis.

.. code:: bash

   racoon_clip -h

Furthermore, racoon_clip provides built-in test commands to verify your installation:

**Light Test (Quick verification):**

.. code:: bash

   racoon_clip test --light

This runs a quick test doing basic functionality checks

**Full Test (Comprehensive verification):**

.. code:: bash

   racoon_clip test

This runs the complete test suite including:

- All tests from the light test
- Full workflow execution tests with example data



Use Docker Image
---------------------
.. _tutorial_container:

If your system has Docker or Apptainer installed, you can also use the racoon_clip Docker Image. Slurm job scheduling of the racoon_clip jobs is not supported by the Docker image. At the moment, usage of SingularityCE containers is also not supported.

.. code:: bash

   docker pull melinak/racoon_clip:latest
   or
   apptainer pull racoon_clip.sif docker://melinak/racoon_clip:latest

We also provide a quick explanation on how to :ref:`use racoon_clip inside a container <tutorial_container>`.



