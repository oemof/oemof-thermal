.. _theoretical_considerations:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Aggregation of domestic decentral solar thermal systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this section the aggregation of consumers using solar thermal systems is discussed. Depending on the consumers energy usage the ratio of heat load and collector
size or storage capacity differs. If you want to model a district with domestic solar systems, it is difficult to aggregate them because of the different sizes of the components and thus different points in time, when the backup heating has to start. The picture shows a scheme of such a system:

.. 	figure:: _pics/aggregation_scheme.png
   :width: 70 %
   :alt: aggregation_scheme.png
   :align: center

Concept
_______


Instead of aggregate all storages and all collectors of the system, which would be really unaccurate, we want to classify two different types of domestic solar systems:

- systems for hot water provision
- systems for hot water provision and space heating support

The system shown in the picture can be characterized by two ratios:

:math:`ratio 1 = \frac{V_{storage}}{A_{collector}} \quad \textrm{and} \quad ratio 2 = \frac{A_{collector}}{\dot{Q}_{demand,max}}`

or, also possible:

:math:`ratio 1 = \frac{V_{storage}}{A_{collector}} \quad \textrm{and} \quad ratio 2 = \frac{A_{collector}}{Q_{demand}}`

Normally there are typical ratios which are used when dimensioning these types of systems.
So it is possible to aggregate the houses within one type by defining these ratios. This would be more accurate than an aggregation of all installed systems.
In case of special system modifications, also more than two groups could be defined.

Nomenclature
____________

    ============================= =============================================
    symbol                        explanation
    ============================= =============================================
    :math:`\dot{Q}_{add}`         Heat flow from external to consumer

    :math:`\dot{Q}_{demand}`      Heat flow demand of the consumer 

    :math:`\dot{Q}_{solar}`       Heat flow from collector

    :math:`\dot{Q}_{demand,max}`  Maximal value of the consumer's heat flow
                                  demand

    :math:`Q_{demand}`            Total demand

    :math:`V_{storage}`           Storage volume

    :math:`A_{collector}`         Collector surface

    ============================= =============================================
