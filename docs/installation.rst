Installation
=========================


Install from GitHub
---------------------

Download the zip file of your prefered release from github and unzip it. Then go into the unziped folder.

.. code:: bash

   unzip racoon_clip-1.0.2.zip
   cd racoon_clip-1.0.2


It is recommended to install racoon_clip it a fresh conda enviroment.

.. code:: bash

   conda create -n racoon_clip pip
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

