.. _tutorial_container:

Using racoon_clip in containers
===============================

Containers isolate their filesystem from the host. Every directory containing
inputs, reference files, configuration files, or outputs must therefore be
available through a bind mount. Slurm scheduling from the provided container
image is not supported.

Pull an image
-------------

.. code:: bash

    docker pull <racoon_clip_image>

Create a host directory
-----------------------

Place or link the analysis inputs and configuration below one directory when
possible. This reduces the number of mounts that must be maintained.

.. code:: bash

    mkdir -p racoon_clip_bindmount

Start the container
-------------------

.. code:: bash

    docker run -it \
        -v /path/to/racoon_clip_bindmount:/racoon_clip_bindmount \
        <racoon_clip_image>

For Docker, ``-v`` maps ``host_directory:container_directory``. Apptainer
provides the equivalent ``--bind`` option. Paths in the analysis
configuration must use the container side of each mapping.

Verify the command
------------------

.. code:: bash

    racoon_clip --version
    racoon_clip test --light

The light test checks basic configuration and workflow construction without
running the complete example suite.
