.. _examples_label:

Examples
========

In this section we provide several examples to demonstrate how you can use the
functions and components of *oemof.thermal*:
[Exapmle Repository](https://github.com/oemof/oemof-thermal/tree/dev/examples)
Among others: 

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

https://github.com/oemof/oemof-thermal/tree/dev/examples/concentrating_solar_power

This example shows the difference between the new approach and a fix efficiency.
The therefor calculated collectors efficiency and irradiance are once depending on
the default loss method and once on the loss method 'Andasol.

It also shows the functionality of the concentrating solar thermal collector and of the ParabolicTroughCollector facade.
This application models a csp plant, to meet an electrical demand. The plant
itself consists of a parabolic trough collector field, a turbine, and a storage.
The collector is build with the facade, which can be found in the facade modul.


**Compression heat pumps and chillers**

https://github.com/oemof/oemof-thermal/tree/dev/examples/compression_heatpumps_and_chiller

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

https://github.com/oemof/oemof-thermal/tree/dev/examples/solar_thermal_collector

In this example the functionality of the solar thermal collector is shown. 
Once with a fixed collector size (aperture area), once with a fixed collector size using the facade and another time with a collector size to be invested.
It also provides plots which can be called by the flat_plate_collector_example.py.

**Stratified thermal storage**

https://github.com/oemof/oemof-thermal/tree/dev/examples/stratified_thermal_storage

This example explains how to use the functions of oemof.thermal's stratified thermal storage module
to specify a storage in a model that optimizes operation with oemof.solph. As well as how to use the facade class StratifiedThermalStorage to add a storage.

Furthermore it shows how to invest into nominal_storage_capacity and capacity
(charging/discharging power) with a fixed ratio and independently with no fixed ratio (There is still a fixed ratio between input and output capacity).




List of Available Models
________________________

