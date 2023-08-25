Installation
=========================


install from GitHub
---------------------

Download the zip file of your prefered release from github and unzip it. Then go into the unziped folder.

.. code-block:: console

   unzip racoon_clip-1.0.0.zip
   cd racoon_clip-1.0.0


It is recommended to install racoon_clip it a fresh conda enviroment.

.. code-block:: console

   conda create -n racoon_clip pip
   conda activate racoon_clip
   conda install -c conda-forge mamba

The install racoon with pip.

.. code-block:: console

   pip install -e .

   # inside a conda env, to avoid pip clashes: Find your anaconda directory, and find the actual venv folder. It should be somewhere like /anaconda/envs/venv_name/.
   /anaconda/envs/venv_name/bin/pip install -e .

You can now check the installation by running help option or and the tutorial :doc:`tutorial.rst`.

.. code-block:: console

   racoon_clip -h

