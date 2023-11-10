Installation
=========================


Install from GitHub
---------------------

Download the zip file of your preferred release from GitHub and unzip it. Then go into the unzipped folder.

.. code:: bash

   wget https://github.com/ZarnackGroup/racoon_clip/archive/refs/tags/v1.0.4.zip
   unzip racoon_clip-1.0.4.zip
   cd racoon_clip-1.0.4


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

