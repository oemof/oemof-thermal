.. _getting_started_label:

~~~~~~~~~~~~~~~
Getting started
~~~~~~~~~~~~~~~

oemof.thermal is an oemof library with a focus on thermal energy technologies (heating/cooling).
In its original intention it is an extension to the components of the optimization framework
oemof.solph. However, some of its functions may be useful for their own.

oemof.thermal is organized like this:

For each technology that is covered, there is a module which holds a collection of useful functions.
These functions can be applied to perform pre-calculations of an optimization model or postprocess
optimization results. Besides, they may equally well be used stand-alone (totally independent from
optimization).

For each module, there is a page that explains the scope of the module and its underlying concept.
Mathematical symbols for commonly used variables and their names in the code are presented in
overview tables. The usage of the functions and some sample results are given. Lastly, notable
references to the literature are listed that the reader can refer to if she wants to get more
information on the background.

Finally, there are a couple of examples that can give an idea of how the functionality of
oemof.thermal can be utilized.

.. contents:: `Contents`
    :depth: 1
    :local:
    :backlinks: top

Using oemof-thermal
===================

Installation
------------

Install oemof-thermal from pypi:

::

    pip install oemof.thermal

Installing the latest (dev) version
-----------------------------------

Clone oemof-thermal from github:

::

    git clone git@github.com:oemof/oemof-thermal.git


Now you can install it your local version of oemof-thermal using pip:

::

    pip install -e <path/to/oemof-thermal/root/dir>

Examples
--------

We provide examples described in the section :ref:`examples_label`.


Contributing to oemof.thermal
=============================

Contributions are welcome. You can write issues to announce bugs or errors or to propose
enhancements. Or you can contribute a new approach that helps to model thermal energy
systems. If you want to contribute, fork the project at github, develop your features on a new
branch and finally open a pull request to merge your contribution to oemof-thermal.

As oemof-thermal is part of the oemof developer group we use the same developer rules, described
`here <http://oemof.readthedocs.io/en/stable/developing_oemof.html>`_.
