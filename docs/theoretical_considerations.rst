.. _theoretical_considerations:

~~~~~~~~~~~~~~~~~~~~~~~~~~
Theoretical considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~


Aggregation of domestic decentral solar thermal systems
_______________________________________________________

In this section the aggregation of consumers using solar thermal systems is discussed. Depending on the consumers energy usage the ratio of heat load and collector
size or storage capacity differs. If you want to model a district with domestic solar systems, it is difficult to aggregate them because of the different sizes of the components and thus different points in time, when the backup heating has to start. The picture shows a scheme of such a system:

.. 	figure:: _pics/aggregation_scheme.png
   :width: 70 %
   :alt: aggregation_scheme.png
   :align: center

Concept
_______


Instead of aggregate all storages and all collectors of the systems, which would be really unaccurate, we want to classify two different types of domestic solar systems:

- systems for hot water provision
- systems for hot water provision and space heating support

The system shown in the picture can be characterized by two ratios:

:math:`ratio_{1} = \frac{V_{storage}}{A_{collector}} \quad \textrm{and} \quad ratio_{2} = \frac{A_{collector}}{\dot{Q}_{demand,max}}`

or, also possible:

:math:`ratio_{1} = \frac{V_{storage}}{A_{collector}} \quad \textrm{and} \quad ratio_{2} = \frac{A_{collector}}{\dot{Q}_{total}}`

Normally there are typical ratios which are used when dimensioning these types of systems.
So it is possible to aggregate the houses within one type by defining these ratios. This would be more accurate than an aggregation of all installed systems.
In case of special system modifications, also more than two groups could be defined.
