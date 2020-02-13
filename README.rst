|badge_pypi| |badge_travis| |badge_docs| |badge_coverage| |link-latest-doi|

#############
oemof.thermal
#############

This package provides tools to model thermal energy components as an extension of
oemof.solph, e.g. compression heat pumps, concentrating solar plants, thermal
storages and solar thermal collectors.

.. contents::

About
=====

The aim of oemof.thermal is to create a toolbox for building models of
thermal energy systems. Modeling thermal energy systems requires specific preprocessing
and postprocessing steps whose detail exceeds the generic formulation of components in
oemof.solph. Currently, most of the functions collected here are intended to be used
together with oemof.solph. However, in some instances they may be useful independently
of oemof.solph.

oemof.thermal is rather new and under active development. Contributions are welcome.

Quickstart
==========

Install oemof.thermal by running

.. code:: bash

    pip install oemof.thermal

in your virtualenv. In your code, you can import modules like e.g.:

.. code:: python

    from oemof.thermal import concentrating_solar_power

Also, have a look at the
`examples <https://github.com/oemof/oemof-thermal/tree/dev/examples>`_.

Documentation
=============

Find the documentation at `<https://oemof-thermal.readthedocs.io>`_.

Contributing
============

Everybody is welcome to contribute to the development of oemof.thermal. The `developer
guidelines of oemof <https://oemof.readthedocs.io/en/stable/developing_oemof.html>`_
are in most parts equally applicable to oemof.thermal.

License
=======

MIT License

Copyright (c) 2019 oemof developing group

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


.. |badge_pypi| image:: https://badge.fury.io/py/oemof.thermal.svg
    :target: https://badge.fury.io/py/oemof.thermal
    :alt: PyPI version

.. |badge_docs| image:: https://readthedocs.org/projects/oemof-thermal/badge/?version=stable
    :target: https://oemof-thermal.readthedocs.io/en/stable/
    :alt: Documentation status

.. |badge_coverage| image:: https://coveralls.io/repos/github/oemof/oemof-thermal/badge.svg?branch=dev&service=github
    :target: https://coveralls.io/github/oemof/oemof-thermal?branch=dev
    :alt: Test coverage

.. |badge_travis| image:: https://travis-ci.org/oemof/oemof.svg?branch=dev
    :target: https://travis-ci.org/oemof/oemof-thermal
    :alt: Build status

.. |link-latest-doi| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3606385.svg
    :target: https://doi.org/10.5281/zenodo.3606385
    :alt: Zenodo DOI
