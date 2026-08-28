.. _installation:

Installation
============

Install from GitHub
-------------------

Choose a release from the
`GitHub release page <https://github.com/ZarnackGroup/racoon_clip/releases>`_,
download its archive, and enter the extracted directory.

.. code-block:: bash

   wget https://github.com/ZarnackGroup/racoon_clip/archive/refs/tags/[version].zip
   unzip [version].zip
   cd racoon_clip-[version]

Create a dedicated environment. RaccoonClip currently expects Python 3.9.0
and Mamba 1.x.

.. code-block:: bash

   conda create -n racoon_clip \
     --override-channels -c conda-forge \
     mamba=1 \
     'python_abi=*=*cp*' \
     python=3.9.0 \
     pip=25.0
   conda activate racoon_clip

If Mamba 1.x is already available, the environment can instead be created
with:

.. code-block:: bash

   mamba create -n racoon_clip python=3.9.0 pip=25.0
   mamba activate racoon_clip

Install the package from the extracted release directory:

.. code-block:: bash

   pip install -e .

If ``pip`` resolves to a different environment, invoke the environment's
executable directly:

.. code-block:: bash

   /anaconda/envs/racoon_clip/bin/pip install -e .

Verify the installation
-----------------------

Confirm that the command is available:

.. code-block:: bash

   racoon_clip -h

The light test performs configuration and DAG checks without running the full
example workflows:

.. code-block:: bash

   racoon_clip test --light

The default test command runs the complete test suite and is more
computationally demanding:

.. code-block:: bash

   racoon_clip test

Additional focused test modes are available:

``--mir``
   Run the miR-eCLIP crosslink and peak tests.

``--groups``
   Test experiment-group handling.

``--fastqscreen``
   Test the optional FastQ Screen path.

``--no-clean``
   Preserve generated result directories for inspection.

Installation errors mentioning ``libmamba`` commonly indicate that Mamba is
missing or is newer than the supported 1.x series. See
:doc:`troubleshooting`.

Containers
----------

Prebuilt Docker images can also be used with Docker or Apptainer:

.. code-block:: bash

   docker pull melinak/racoon_clip:latest
   or
   apptainer pull racoon_clip.sif docker://melinak/racoon_clip:latest

Container users must bind their input, reference, and output directories into
the container. Continue with :doc:`tutorial_container`.

