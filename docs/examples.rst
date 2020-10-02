.. _examples_label:

Examples
========

In this section we provide several examples to demonstrate how you can use the
functions and components of *oemof.thermal*:
https://github.com/oemof/oemof-thermal/tree/dev/examples

- functionality of collector facade and efficency calculation 
- calculation of max possible heat output
- functionality of solar thermal collectors
- investment decision on thermal storage and capacity

Most of the examples show the usage of *oemof.thermal* together with *oemof.solph*.
However, *oemof.thermal* is a stand-alone package and you can
use the package and its calculations in any other context as well.

List of Available Examples
__________________________

**Concentrating solar power (CSP)**

This example shows the difference between the new approach and a fix efficiency.
The therefor calculated collectors efficiency and irradiance are once depending on
the default loss method and once on the loss method 'Andasol.

It also shows the functionality of the concentrating solar thermal collector and of the ParabolicTroughCollector facade.
This application models a csp plant, to meet an electrical demand. The plant
itself consists of a parabolic trough collector field, a turbine, and a storage.
The collector is build with the facade, which can be found in the facade modul


**Compression heat pumps and chillers**

A different example provides an "how to" on the use of the 'calc_cops' function to get the
COPs of an exemplary air-source heat pump (ASHP). It also shows how to use the
pre-calculated COPs in a solph.Transformer.
Furthermore, the maximal possible heat output of the heat pump is
pre-calculated and varies with the temperature levels of the heat reservoirs.
In the exapmle the ambient air is used as low temperature heat reservoir.

It will also be explained how to use the 'calc_cops' function to get the
COPs of a compression chiller using pd.Time-Series as input.
Therefor the ambient air is used as heat sink (high temperature reservoir). 
The input is a list to show how the function can be applied on several time steps. 
The output is a list as well and may serve as input (conversion_factor) for a
oemof.solph.transformer.

In addition to that the example provides a manual on useing the 'calc_cops' function 
to get the COPs of a heat pump, by ploting the temperature dependency of the COP, and COPs of an exemplary ground-source heat pump (GSHP)
useing the soil temperature as low temperature heat reservoir.

**Solar thermal collector**

- flat_plate_collector_example [1]_
- plots

**Stratified thermal storage**

- stratified thermal storage [1]_
- stratified thermal storage (investment mode) [1]_
- plots



List of Available Models
________________________

