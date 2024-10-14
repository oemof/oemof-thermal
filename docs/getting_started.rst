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

To help setting up more detailed components in a simple way, oemof.thermal provides facades based on the
`oemof.tabular.facades module <https://oemof-tabular.readthedocs.io/en/stable/reference/oemof.tabular.html>`_.
Facades are classes that offer a simpler interface to more complex classes. More specifically, the :class:`Facade` s
in this module inherit from `oemof.solph`'s generic classes to serve as more concrete and energy specific interface.
The concept of the facades has been derived from oemof.tabular. The idea is to be able to
instantiate a :class:`Facade` using only keyword arguments. Under the hood the :class:`Facade` then
uses these arguments to construct an `oemof.solph` component and sets it up to be easily used in an
:py:obj:`EnergySystem`. Usually, a subset of the attributes of the parent class remains while another
part can be addressed by more specific or simpler attributes. In oemof.thermal, some of the technologies have a facade class
that can be found in the module oemof.thermal.facades. See the
:ref:`api reference for the facade module <api_label>` for further information on the structure of
these classes.

For each module, there is a page that explains the scope of the module and its underlying concept.
Mathematical symbols for commonly used variables and their names in the code are presented in
overview tables. The usage of the functions and some sample results are given. Lastly, notable
references to the literature are listed that the reader can refer to if she wants to get more
information on the background.

Finally, there are a couple of examples that can give an idea of how the functionality of
oemof.thermal can be utilized. Some models have undergone validation whose results you'll find
in the section "Model validation".

.. contents:: `Contents`
    :depth: 1
    :local:
    :backlinks: top

Using oemof.thermal
===================

Installation
------------

Install oemof.thermal from pypi:

::

    pip install oemof.thermal

Installing the latest (dev) version
-----------------------------------

Clone oemof.thermal from github:

::

    git clone git@github.com:oemof/oemof-thermal.git


Now you can install your local version of oemof.thermal using pip:

::

    pip install -e <path/to/oemof-thermal/root/dir>

Examples
--------

We provide examples described in the section :ref:`examples_label`.
Further we developed some complex models with the oemof-thermal components
which are described in this section as well.


Contributing to oemof.thermal
=============================

Contributions are welcome. You can write issues to announce bugs or errors or to propose
enhancements. Or you can contribute a new approach that helps to model thermal energy
systems. If you want to contribute, fork the project at github, develop your features on a new
branch and finally open a pull request to merge your contribution to oemof.thermal.

As oemof.thermal is part of the oemof developer group we use the same developer rules,
described in the `oemof documentation <https://oemof.readthedocs.io/en/latest/>`_.
