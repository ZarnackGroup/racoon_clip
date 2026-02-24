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

.. Note::

    The ``-v`` flag in Docker or ``--bind`` in Apptainer performs the
    binding of a mounted directory. The syntax is:: ``folder/on/your/system:/folder/in/the/container``



Check that ``racoon_clip`` works
-----------------------------------

Get the version number.

.. code:: commandline

    racoon_clip --version

Test racoon_clip

.. code:: commandline 

    racoon_clip test --light

This runs a quick test including basic functionality checks and should
output the message: "All tests passed successfully!"


