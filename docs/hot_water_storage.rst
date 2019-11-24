.. _hot_water_storage_label:

~~~~~~~~~~~~~~~~~
Hot water storage
~~~~~~~~~~~~~~~~~

A simplified 2-zone-model of a stratified thermal energy storage.

.. 	image:: _pics/stratified_thermal_storage.svg
   :width: 70 %
   :alt: stratified_thermal_storage.svg
   :align: center

* We assume a cylindrical storage with of diameter d and height h,
  with two temperature regions that are perfectly separated.
* The temperatures are assumed to be constant and correspond to
  the feedin/return temperature of the heating system.
* Heat conductivity of the storage has to be passed as well as a timeseries
  for outside temperatures for the calculation of heat losses.
* There is no distinction between outside temperature and ground temperature.
* Material properties are constant.

The equation describing the change of storage content is the following:

.. math::
  Q_t = Q_{t-1} - UA \Bigg(\frac{Q_t-1}{Q_N} \Delta T_{HC} + \Delta T_{C0}\Bigg)\Delta t
  + \dot{Q}_{in,t}\eta_{in}\Delta t - \frac{\dot{Q}_{out}}{\eta_{out}}\Delta t.

In the case of investment, the diameter d is given and the height can be
adapted to adapt the nominal capacity of the storage. With this assumption,
all relations stay linear.

These parameters are input to the component:

    ========================= ==================================================== ==== =========
    symbol                    attribute                                            type explanation
    ========================= ==================================================== ==== =========
    :math:`h`                 :py:obj:`height`                                          Height (if not investment)

    :math:`d`                                                                           Diameter

    :math:`\rho`                                                                        Density of storage medium

    :math:`c`                                                                           Heat capacity of storage medium

    :math:`T_H`                                                                         Hot temperature level

    :math:`T_C`                                                                         Cold temperature

    :math:`T_0`                                                                         Environment temperature
                                                                                        timeseries

    :math:`U`                                                                           Thermal transmittance

    :math:`\eta_{in}`                                                                   Charging efficiency

    :math:`\eta_{out}`                                                                  Discharging efficiency

    :math:`\beta`                                                                       Factor describing the usable
                                                                                        storage volume
                                                                                        (:math:`0<\beta<1`)

    :math:`s_{iso}`:          :py:obj:`s_iso`                                           Thickness of isolation layer

    :math:`\lambda_{iso}`:    :py:obj:`height`                                          Heat conductivity of isolation material

    :math:`\alpha_{inside}`:  :py:obj:`height`                                          Heat transfer coefficient inside

    :math:`\alpha_{outside}`: :py:obj:`height`                                          Heat transfer coefficient outside

    ========================= ==================================================== ==== =========


The thermal transmittance is precalculated using `calculate_u_value`.

.. code-block:: python

    u_value = calculate_storage_u_value()

.. include:: ../src/oemof/thermal/stratified_thermal_storage.py
  :start-after:  calculate_storage_u_value-equations:
  :end-before: Parameters

The nominal storage capacity, minimum and maximum storage level are precalculated upon initialization
using `calculate_capacities`.

.. code-block:: python

   nominal_storage_capacity, surface, max_storage_level, min_storage_level = calculate_capacities()

.. .. include:: ../src/oemof/thermal/stratified_thermal_storage.py
  :start-after:  calculate_capacities-equations:
  :end-before: Parameters

.. include:: ../src/oemof/thermal/stratified_thermal_storage.py
  :start-after:  calculate_capacities-equations:
  :end-before: Parameters

Loss terms are precalculated by the following function.

.. code-block:: python

    loss_rate, fixed_losses = calculate_losses()


.. include:: ../src/oemof/thermal/stratified_thermal_storage.py
  :start-after:  calculate_losses-equations:
  :end-before: Parameters

Finally, the parameters can be used to define a storage component.

.. code-block:: python

    thermal_storage = oemof.solph.GenericStorage(
        label='thermal_storage',
        inputs={bus_heat: Flow()},
        outputs={bus_heat: Flow()},
        nominal_storage_capacity=nominal_storage_capacity,
        min_storage_level=min_storage_level,
        max_storage_level=max_storage_level,
        loss_rate=loss_rate,
        fixed_losses=fixed_losses,
        inflow_conversion_factor=1.,
        outflow_conversion_factor=1.
    )


For investment, :math:`Q_N` is not fixed in advance.
:math:`A = \pi d h + 2 \pi \frac{d^2}{4}` The same as for :math:`Q_N` applies to :math:`A`

Variables:

:math:`Q_t`: Storage level at time :math:`t`
:math:`\dot{Q}_{in,t}`: Charging power at time :math:`t`
:math:`\dot{Q}_{out,t}`: Discharging power at time :math:`t`
:math:`Q_N`, in case of investment

The following constraints are implemented:

:math:`Q_t >= Q_{min}`

:math:`Q_t <= Q_{max}`

:math:`Q_t = Q_{t-1} - UA(\frac{Q_t-1}{Q_N} \Delta T_{HC} + \Delta T_{C0})\Delta t + \dot{Q}_{in,t}\eta_{in}\Delta t - \frac{\dot{Q}_{out}}{\eta_{out}}\Delta t`

These two constraints apply in case of investment optimization:

:math:`A = \frac{4 Q_N}{d \cdot c \cdot \rho \cdot \Delta T_{HC}} + \frac{d^2}{2} \cdot \pi`
:math:`h = \frac{Q_N}{\frac{d^2}{4} \cdot \pi \cdot c \cdot \rho \cdot \left( T_{H} - T_{C} \right)}`
