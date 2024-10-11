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

List of available examples
__________________________

**Compression heat pump and chiller**

An example provides an "how to" on the use of the 'calc_cops' function to get the
coefficients of performance (COP) of an exemplary air-source heat pump (ASHP). It also shows how to use the
pre-calculated COPs in a solph.Converter.
Furthermore, the maximal possible heat output of the heat pump is
pre-calculated and varies with the temperature levels of the heat reservoirs.
In the example the ambient air is used as low temperature heat reservoir.

In addition to that, the example provides a manual on using the 'calc_cops' function
to get the COPs of a heat pump, by plotting the temperature dependency of the COP, and COPs of an exemplary
ground-source heat pump (GSHP) using the soil temperature as low temperature heat reservoir.

The Examples can be found `at compression_heatpumps_and_chiller <https://github.com/oemof/oemof-thermal/tree/master/examples/compression_heatpump_and_chiller>`_.

**Absorption Chiller**

The first example shows the behaviour of the coefficient of performance and heat flows such as the cooling capacity
for different cooling water temperatures based on the characteristic equation method.
The second example underlines the dependence of the temperature of the cooling water on the cooling capacity.

The Examples can be found `at absorption_heatpumps_and_chiller <https://github.com/oemof/oemof-thermal/tree/master/examples/absorption_heatpump_and_chiller>`_.

**Concentrating solar power (CSP)**

These examples shows the difference between the new approach of the oemof-thermal component and a fix efficiency.
The collector's efficiency and irradiance can be calculated with two different loss methods. The examples also shows the functionalitiy of the ParabolicTroughCollector facade.

An application is presented which models a csp plant to meet an electrical demand. The plant
itself consists of a parabolic trough collector field, a turbine, and a storage.

The Examples can be found `at concentrating_solar_power <https://github.com/oemof/oemof-thermal/tree/master/examples/concentrating_solar_power>`_.

**Solar thermal collector**

In these examples the functionality of the solar thermal collector is shown. 
Once with a fixed collector size (aperture area), once with a fixed collector size using the facade and another time with a collector size to be invested.
It also provides plots which can be called by the flat_plate_collector_example.py.

The Examples can be found `at solar_thermal_collector <https://github.com/oemof/oemof-thermal/tree/master/examples/solar_thermal_collector>`_.

**Stratified thermal storage**

These example explain how to use the functions of oemof-thermal's stratified thermal storage module
to specify a storage in a model that optimizes operation with oemof-solph. Further it is shown how to use the facade class StratifiedThermalStorage.

Furthermore the examples show how to invest into nominal_storage_capacity and capacity
(charging/discharging power) with a fixed ratio and independently with no fixed ratio.

The Examples can be found `at stratified_thermal_storage <https://github.com/oemof/oemof-thermal/tree/master/examples/stratified_thermal_storage>`_.

**Cogeneration**

We further provide an example on different emission allocation methods in cogeneration.
This Example can be found `at cogeneration <https://github.com/oemof/oemof-thermal/tree/master/examples/cogeneration>`_.


List of available models
________________________

In the `GitHub organisation of the oemof_heat project <https://github.com/oemof-heat/solar_models>`_ you will find more complex models which use the components "solar_thermal_collector" and "concentrating_solar_power" from oemof_thermal.

**Solar Cooling Model**

The application models a cooling system for a building with a given cooling demand.

**Desalination Model**

The application models a desalination system with a given water demand.





