.. _absorption_chillers_label:


~~~~~~~~~~~~~~~~~~~~~~~
Absorption chillers
~~~~~~~~~~~~~~~~~~~~~~~

Calculations for absorption chillers based on the characteristic equation method.


Motivation and possible application
___________________________________

This module was developed to provide cooling capacity and COP calculations
based on temperatures for energy system optimizations with oemof.solph.

A time series of pre-calculated COPs and cooling capacity values can be used
as input for a transformer(an oemof.solph component) in an
energy system optimization.
Discover more possibilities to use this module with our examples.


Concept
_______

A characteristic equation model to describe the performance of
absorption chillers.

The cooling capacity (:math:`\dot{Q}_{E}`) is determined by a function of
the characteristic
temperature difference (:math:`\Delta\Delta T`) that combines the external
mean temperatures of the heat exchangers.

Various approaches of the characteristic equation method exists.
Here we use the approach described by Kühn and Ziegler.

.. math::
  \Delta\Delta T = t_{G} - a \cdot t_{AC} + e \cdot t_{E}

where :math:`t` is the external mean fluid temperature of the heat exchangers
(G: Generator, AC: Absorber and Condenser, E: Evaporator)
and :math:`a` and :math:`e` are characteristic parameters.

The cooling capacity (:math:`\dot{Q}_{E}`) and the driving
heat (:math:`\dot{Q}_{G}`) can be expressed as linear functions of :math:`\Delta\Delta T`:

.. math::
  \dot{Q}_{E} = s_{E} \cdot \Delta\Delta T + r_{E}

.. math::
  \dot{Q}_{G} = s_{G} \cdot \Delta\Delta T + r_{G}

with the characteristic parameters :math:`s_{E}`, :math:`r_{E}`,
:math:`s_{G}`, and :math:`r_{G}`.

The COP is then calculated from :math:`\dot{Q}_{E}` and :math:`\dot{Q}_{G}`:

.. math::
  COP = \frac{\dot{Q}_{E}}{\dot{Q}_{G}}





