#! /usr/bin/env python
# -*- encoding: utf-8 -*-
"""
This file is part of project oemof-thermal (github.com/oemof/oemof-thermal). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location oemof-thermal/setup.py
"""

from setuptools import find_packages, setup
import os

import oemof


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='oemof.thermal',
    # version=oemof.thermal.__version__,
    author='oemof developer group',
    description='Thermal energy components for oemof',
    url='https://github.com/oemof/oemof-thermal',
    packages=["oemof"] + ["oemof." + p for p in find_packages("src/oemof")],
    package_dir={"": "src"},
    namespace_package=['oemof.thermal'],
    long_description=read('README.rst'),
    install_requires=[],
    extras_require={}
)