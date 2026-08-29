.. _tutorial_container:

Using racoon_clip in containers
===============================

Containers isolate their filesystem from the host. A racoon_clip docker image is available from `melinak/racoon_clip <https://hub.docker.com/r/melinak/racoon_clip/tags>`_.

.. Note:

- Every directory containing inputs, reference files, configuration files, or outputs must be
available through a bind mount. 
- Slurm scheduling from the provided container image is not supported.

Pull an image
-------------

Choose either Docker or Apptainer.

Docker
~~~~~~

.. code-block:: bash

   docker pull melinak/racoon_clip:latest

Apptainer
~~~~~~~~~

Pull the Docker image and save it as an Apptainer ``.sif`` file:

.. code-block:: bash

   apptainer pull racoon_clip_latest.sif docker://melinak/racoon_clip:latest

.. note::

   SingularityCE is not supported. Use Apptainer when running racoon_clip on
   systems without Docker.

Create a host directory
-----------------------

Place or link the analysis inputs and configuration below one directory when
possible. This reduces the number of mounts that must be maintained.

.. code:: bash

    mkdir -p racoon_clip_bindmount

Start the container
-------------------
Choose the command for your container runtime.

Docker
~~~~~~

.. code-block:: bash

   docker run -it \
       -v /path/to/racoon_clip_bindmount:/racoon_clip_bindmount \
       melinak/racoon_clip:latest

Apptainer
~~~~~~~~~

.. code-block:: bash

   apptainer shell \
       --bind /path/to/racoon_clip_bindmount:/racoon_clip_bindmount \
       racoon_clip_latest.sif


For Docker, ``-v`` maps ``host_directory:container_directory``. Apptainer
provides the equivalent ``--bind`` option. Paths in the analysis
configuration must use the container side of each mapping.

Verify the command
------------------

Inside the container, run

.. code:: bash

    racoon_clip --version
    racoon_clip test --light


