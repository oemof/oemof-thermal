.. _compression_heat_pumps_label:

Compression Heat Pumps and Chillers
===================================

Simple calculations for compression heat pumps and chillers.

Compression heat pumps and chillers increase the temperature of a flow using
a compressor that consumes electric power.
The inlet heat flux comes from a low temperature heat reservoir (T\_low) and the
outlet has the temperature level of the high
temperature heat reservoir (T\_high).
The same cycle can be used for heating (heat pump) or
cooling (chiller).


.. figure:: _pics/heatpump_col.png
    :width: 40 %
    :alt: heatpump_col.png
    :align: center
    :figclass: align-center

    Fig.1: The heat pump cycle and its two temperature levels.

The efficiency of the heat pump cycle process can be described by
the Coefficient of Performance (COP).
The COP describes the ratio of useful heat (:math:`\dot{Q}_\mathrm{in}` or :math:`\dot{Q}_\mathrm{out}`) per
electric work consumed:

.. math::
        COP = \frac{\dot{Q}_\mathrm{useful}}{P_\mathrm{el}}

The Carnot efficiency :math:`COP_\mathrm{Carnot}` describes the maximum
theoretical efficiency.
It depends on the temperature of the two heat reservoirs.

.. math::
        COP_\mathrm{Carnot} = \frac{T_\mathrm{high}}{T_\mathrm{high} - T_\mathrm{low}}

To determine the real COP of a machine a factor, the quality grade,
is applied on the Carnor Efficiency:

.. math::
        COP = \eta \cdot COP_\mathrm{Carnot}


.. figure:: _pics/cop_dependence_on_temp_difference.png
    :width: 70 %
    :alt: cop_dependence_on_temp_difference.png
    :align: center
    :figclass: align-center

    Fig.2: COP dependence on temperature difference
    (Output of example `cop_dependence_on_temperature_difference.py`).



These parameters are input to the functions:

    ============================= ============================== ==== =============================
    symbol                        attribute                      type explanation
    ============================= ============================== ==== =============================
    :math:`COP`                   :py:obj:`cop`                         Coefficient of Performance

    :math:`T_\mathrm{high}`       :py:obj:`temp_high`                   Temperature of the high temp. heat reservoir

    :math:`T_\mathrm{low}`        :py:obj:`temp_low`                    Temperature of the low temp. heat reservoir

    :math:`\eta`                  :py:obj:`quality_grade`               Quality grade

    :math:`T_\mathrm{icing}`      :py:obj:`temp_threshold_icing`        Temperature below which icing occurs

    :math:`f_\mathrm{icing}`      :py:obj:`factor_icing`                COP reduction caused by icing
    ============================= ============================== ==== =============================



The Coefficient of Performance (COP) is calculated using `calc_cops()`.

.. code-block:: python

    COP = calc_cops(temp_high,
                    temp_low,
                    quality_grade,
                    temp_threshold_icing,
                    consider_icing,
                    factor_icing,
                    mode)

.. include:: ../src/oemof/thermal/compression_heatpumps_and_chillers.py
  :start-after:  calc_cops-equations:
  :end-before: Parameters

The maximum cooling capacity can be calculated using `calc_max_Q_dot_chill()`.

.. code-block:: python

    Q_dot_chill_max = calc_max_Q_dot_chill(nominal_conditions, cops)

.. include:: ../src/oemof/thermal/compression_heatpumps_and_chillers.py
  :start-after:  calc_max_Q_dot_chill-equations:
  :end-before: Parameters

The maximum heating capacity can be calculated using `calc_max_Q_dot_heat()`.

.. code-block:: python

    Q_dot_heat_max = calc_max_Q_dot_heat(nominal_conditions, cops)

.. include:: ../src/oemof/thermal/compression_heatpumps_and_chillers.py
  :start-after:  calc_max_Q_dot_heat-equations:
  :end-before: Parameters

The quality grade at nominal point of operation can be calculated using `calc_chiller_quality_grade()`.
Do NOT use this function to determine the input for `calc_cops()`!

.. code-block:: python

    quality_grade = calc_chiller_quality_grade(nominal_conditions)

.. include:: ../src/oemof/thermal/compression_heatpumps_and_chillers.py
  :start-after:  calc_chiller_quality_grade-equations:
  :end-before: Parameters