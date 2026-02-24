Tutorial: Using racoon_clip inside containers
================================

.. contents:: 
    :depth: 2

Containers run in isolated filesystem environments and therefore require explicit bind mounts to make input data and output directories from the host system accessible inside the container. 
A brief description of how to handle this will be given here. 
Users unfamiliar with containers and container bind mounts are advised to consult the respective documentation or use the GitHub installation instead. 
SingularityCE is not supported at the moment.

Pull a container image of racoon_clip
-----------------------------------

.. code:: commandline

    docker pull <racoon_clip_image>


Make folders for bind mounts.
-----------------------------------
These are the folders that will be bound to the container and pass all
inputs and outputs between your system and the container

.. code:: commandline

    mkdir -p racoon_clip_bindmount


Start a racoon_clip container that mounts the racoon_clip_bindmount folder
-----------------------------------

.. code:: commandline

    docker run -it \
        -v /path/to/racoon_clip_bindmount:/racoon_clip_bindmount \
        <racoon_clip_image>

Note
----

The ``-v`` flag in Docker or ``--bind`` in Apptainer performs the
binding of a mounted directory. The syntax is::

    folder/on/your/system:/folder/in/the/container

If using a different version of ``racoon_clip`` than ``v.2.0.11`` as
used here, adjust the name of the folder in the container to the
correct version number.

2. Check that ``racoon_clip`` works
-----------------------------------

a. Get the version number.

In this protocol, we are using version ``v.2.0.11``::

    racoon_clip --version

(Optional) Test ``racoon_clip``

This runs a quick test including basic functionality checks and should
output the message::

    All tests passed successfully

If not, see the troubleshooting section below::

    racoon_clip test
