Installation
=========================


Install from GitHub
---------------------

Download the zip file of your preferred release from GitHub and unzip it. Then go into the unzipped folder.

.. code:: bash

   unzip racoon_clip-1.0.3.zip
   cd racoon_clip-1.0.3


It is recommended to install racoon_clip in a fresh conda environment.

.. code:: bash

   conda create -n racoon_clip python=3.9.0 pip
   conda activate racoon_clip

Then install racoon with pip.

.. code:: bash

   pip install -e .

   # inside a conda env, to avoid pip clashes: 
   # Find your anaconda directory, and find the actual venv folder. 
   # (It should be somewhere like /anaconda/envs/venv_name/.)

   /anaconda/envs/venv_name/bin/pip install -e .

You can now check the installation by running the help option and the :ref:`tutorial <tutorial>`.

.. code:: bash

   racoon_clip -h

