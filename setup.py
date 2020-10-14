#! /usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import find_packages, setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='oemof.thermal',
      version='0.0.4',
      author='oemof developer group',
      author_email='contact@oemof.org',
      description=(
          'Thermal energy components for '
          'the open energy modelling framework.'
      ),
      url='https://github.com/oemof/oemof-thermal',
      long_description=read('README.rst'),
      packages=["oemof"] + ["oemof." + p for p in find_packages("src/oemof")],
      package_dir={"": "src"},
      install_requires=['oemof.solph',
                        'matplotlib',
                        'pvlib',
                        'numpy >= 1.7.0, < 1.18',
                        'pandas >= 0.18.0, < 0.26'])
