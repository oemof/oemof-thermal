.. _validation_compression_heat_pumps_label:

Compression Heat Pumps and Chillers
===================================

Scope
_____

The validation of the compression heat pump and chiller has been conducted within the
`GRECO project <https://github.com/greco-project>`_.
Monitored data of the two components in combination with PV without storage was provided by Universidad Politécnica de
Madrid (UPM).
The set of data contains amongst others external and internal temperatures of the components and a calculated
COP / EER value.
** TODO: what technology - air to air? **

Method
_______

In order to calculate the COP and EER using oemof.thermal the temperature of the heat source, the temperature of the
heat sink and the quality grade are required. The quality grade describes the relation between the actual
coefficient of performance and the coefficient of performance of the Carnot process. Please see the
`USER'S GUIDE <https://oemof-thermal.readthedocs.io/en/latest/compression_heat_pumps_and_chillers.html>`_ for further
information.
The monitored coefficients from UPM are compared with the coefficients calculated using different quality grades
to evaluate which quality grade fits best the examined chiller and heat pump. For the heat pump, the temperature of the
external input into the evaporator is the heat source and the temperature of the internal output from the condenser
is the heat sink. In case of the chiller the heat source is the external temperature input into the condenser
and the heat sink the internal temperature output from the evaporator. The monitored coefficients are calculated as the
ratio between the thermal capacity and the electrical capacity.

The data set contains data points where the solar modules provide an electrical power less than 100 watts and where the
compressor of the installation is turned off. These data points are excluded from calculations since they differ from
the ones under the operational behavior of the component. For this purpose the data is preprocessed in order to attain
only data points with electrical power greater or equal to 100 watts and with the integral fan turned on.

The functionalities for calculating the COP and EER of oemof.thermal are made for a stationary process, while the data
provided by UPM includes mostly data from non-stationary periods as different control modes are explored. To balance the
fluctuating values we decided to analyze average hourly values.

Various types of charts are used for the validation of the calculated COP and EER. For the validation the residual,
which corresponds to the difference of the monitored and calculated coefficients is used. For both, chiller and heat
pump, correlations with the residual are shown in various types of charts: histograms, correlation between calculated
and monitored coefficients, the root mean square error (RMSE), the relation between the residuals and temperature hub
as well as the relation between residuals and monitored coefficients are reviewed. Graphs showing the relation
between residuals and the temperature hub or monitored coefficients are made to examine a possible dependence.


Results of the chiller
______________________

Typical EER of chillers used for cooling are around 4 to 5 [1]. By adhering to these reference values we conclude
that EERs with quality grades ranging from 0,1 to 0,35 give fitting results.

The RMSE for the validated quality grades presents the standard deviation of the residuals. Among the range of quality
grades for the chiller, the RMSE is the smallest for the quality grade 0,30 with 0.573 and larger for 0,25 with 0.758
and 0.35 with a RMSE of 1.181.

============================= =============================
    Quality grade                   RSME
============================= =============================
    0.05                            3.831
    0.10                            3.030
    0.15                            2.236
    0.20                            1.460
    0.25                            0.758
    0.30                            0.573
    0.35                            1.181
    0.40                            1.943
    0.45                            2.732
    0.50                            3.531
============================= =============================


The correlation with quality grades 0.05 to 0.30 show an overestimation of the coefficients. In contrast,
calculated EER at quality grades above 0.30 indicate an underestimation. Figures 1 and 2 each show an example of
over- and underestimation:

.. figure:: _pics/Correlation_EERs.png
    :width: 100 %
    :alt: Correlation_EERs.png
    :align: center
    :figclass: align-center

    Fig.1: Correlation between monitored and calculated EER with overestimation showing a quality grade of 0.25 (left),
    quality grade of 0.30 with least error and with underestimation connected to a quality grade of 0.35.

The outliers in the monitored data could be due to the start-up and shutdown of the prototypes’ compressor.


Results of the heat pump
________________________



References
__________

[1] Ziegler, D.-I. F. (1997).
Sorptionswärmepumpen.
Erding: Forschungsberichte des Deutschen Kälte- und Klimatechnischen Vereins Nr. 57

