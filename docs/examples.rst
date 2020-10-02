.. _examples_label:

Examples
========

In this section we provide several examples to demonstrate how you can use the
functions and components of *oemof-thermal*. You can find them in the `example folder <https://github.com/oemof/oemof-thermal/tree/master/examples>`_
of the repository.
Among them are the following calculations: 

- Functionality of solar thermal and concentrating solar collector's facade and efficiency calculation 
- Calculation of maximum possible heat output of heat pumps
- Investment decision on thermal storage and capacity

Most of the examples show the usage of *oemof-thermal* together with *oemof-solph*.
However, *oemof-thermal* is a stand-alone package and you can
use the package and its calculations in any other context as well.

List of Available Examples
__________________________

**Compression heat pump and chiller**

A different example provides an "how to" on the use of the 'calc_cops' function to get the
COPs of an exemplary air-source heat pump (ASHP). It also shows how to use the
pre-calculated COPs in a solph.Transformer.
Furthermore, the maximal possible heat output of the heat pump is
pre-calculated and varies with the temperature levels of the heat reservoirs.
In the example the ambient air is used as low temperature heat reservoir.

It will also be explained how to use the 'calc_cops' function to get the
COPs of a compression chiller using pd.Time-Series as input.
Therefor the ambient air is used as heat sink (high temperature reservoir). 
The input is a list to show how the function can be applied on several time steps. 
The output is a list as well and may serve as input (conversion_factor) for an
oemof.solph.transformer.

In addition to that the example provides a manual on using the 'calc_cops' function 
to get the COPs of a heat pump, by plotting the temperature dependency of the COP, and COPs of an exemplary ground-source heat pump (GSHP)
using the soil temperature as low temperature heat reservoir.

The Examples can be found `here <https://github.com/oemof/oemof-thermal/tree/master/examples/compression_heatpumps_and_chiller>`_.

**Concentrating solar power (CSP)**

These examples shows the difference between the new approach of the oemof-thermal component and a fix efficiency.
The collector's efficiency and irradiance can be calculated with two different loss methods. The examples also shows the functionalitiy of the ParabolicTroughCollector facade.

An application is presented which models a csp plant to meet an electrical demand. The plant
itself consists of a parabolic trough collector field, a turbine, and a storage.

The Examples can be found `here <https://github.com/oemof/oemof-thermal/tree/master/examples/concentrating_solar_power>`_.

**Solar thermal collector**

In these examples the functionality of the solar thermal collector is shown. 
Once with a fixed collector size (aperture area), once with a fixed collector size using the facade and another time with a collector size to be invested.
It also provides plots which can be called by the flat_plate_collector_example.py.

The Examples can be found `here <https://github.com/oemof/oemof-thermal/tree/master/examples/solar_thermal_collector>`_.

**Stratified thermal storage**

These example explain how to use the functions of oemof-thermal's stratified thermal storage module
to specify a storage in a model that optimizes operation with oemof-solph. Further it is shown how to use the facade class StratifiedThermalStorage.

Furthermore the examples show how to invest into nominal_storage_capacity and capacity
(charging/discharging power) with a fixed ratio and independently with no fixed ratio.

The Examples can be found `here <https://github.com/oemof/oemof-thermal/tree/master/examples/stratified_thermal_storage>`_.

**Cogeneration**

We further provide an example on different emission allocation methods in cogeneration.

This Example can be found `here <https://github.com/oemof/oemof-thermal/tree/master/examples/cogeneration>`_.


List of Available Models
________________________

In this `section <https://github.com/oemof-heat/solar_models>` you will find more complex models, which use the components "solar_thermal_collector" and "concentrating_solar_power" from oemof_thermal.

**Solar Cooling Model**

The application models a cooling system for a building with a given cooling demand.
https://github.com/oemof-heat/solar_models/tree/master/solar_cooling

**Desalination Model**

The application models a desalination system with a given water demand.







