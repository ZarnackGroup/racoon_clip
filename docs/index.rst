.. racoon_clip documentation master file, created by
   sphinx-quickstart on Wed Aug 23 12:29:06 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to racoon_clip's documentation!
=======================================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   installation
   tutorial 
   all_options
   methods_description



.. note::

   This project is under active development.

racoon_clip - What is it?
=========================

racoon_clip processes your iCLIP and eCLIP data from raw files to single-nucleotide crosslinks in a single step. It is an automation of the iCLIP pipeline pubished by Busch *et al.* 2020 (`iCLIP data analysis: A complete pipeline from sequencing reads to RBP binding sites <https://doi.org/10.1016/j.ymeth.2019.11.008>`_) making the same processing now available for both iCLIP and eCLIP data in a highly reproducible manner. 

The performed steps are a quality filter (optional), demultiplexing (optional), adapter trimming, genome alignment,  deduplication (optional) and selection of single nucleotide crosslinks. For details on the performed steps please see :ref:`Detailed description of steps performed by racoon`.

.. figure:: ../Workflow.png
   :width: 600

   Steps performed by racoon_clip.


Usage
=========================
                                                                                                                                                                                                                                                                            
Once installed you can run racoon with:

.. code:: bash

   racoon_clip run --cores <number_of_cores> --configfile </path/to/config/file.yaml>

                                                                                                                                                            

Requirements
================

- python >3.9
- conda or mamba 
- pip





Citations
=================

- Busch *et al.* 2020 -- `iCLIP data analysis: A complete pipeline from sequencing reads to RBP binding sites <https://doi.org/10.1016/j.ymeth.2019.11.008>`_




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


