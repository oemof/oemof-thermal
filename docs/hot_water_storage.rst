.. _hot_water_storage_label:

~~~~~~~~~~~~~~~~~
Hot water storage
~~~~~~~~~~~~~~~~~

A simplified 2-zone-model of a stratified thermal energy storage.

* We assume a cylindrical storage with of diameter d and height h,
  with two temperature regions that are perfectly separated.
* The temperatures are assumed to be constant and correspond to
  the feedin/return temperature of the heating system.
* Heat conductivity of the storage has to be passed as well as a timeseries
  for outside temperatures for the calculation of heat losses.
* There is no distinction between outside temperature and ground temperature.
* Material properties are constant.

In the case of investment, the diameter d is given and the height can be
adapted to adapt the nominal capacity of the storage. With this assumption,
all relations stay linear.


These parameters are input to the component:

:math:`h`: Height (if not investment)
:math:`d`: Diameter
:math:`\rho`: Density of storage medium
:math:`c`: Heat capacity of storage medium
:math:`T_H`: Hot temperature level
:math:`T_C`: Cold temperature
:math:`T_0`: Environment temperature timeseries
:math:`U`: Thermal transmittance
:math:`\eta_{in}`: Charge efficiency
:math:`\eta_{out}`: Discharge efficiency
:math:`\beta`: Factor describing the usable storage volume (:math:`0<\beta<1`)

The thermal transmittance is precalculated from these parameters:
:math:`s_{iso}`: Thickness of isolation layer
:math:`\lambda_{iso}`: Heat conductivity of isolation material
:math:`\alpha_{inside}`: Heat transfer coefficient inside
:math:`\alpha_{outside}`: Heat transfer coefficient outside

:math:`U = \frac{1}{\frac{1}{\alpha_i} + \frac{s_{iso}}{\lambda_ {iso}} + \frac{1}{\alpha_a}}`

These parameters are calculated upon initialization:

:math:`Q_{max} = Q_N \cdot (1-\beta/2)`
:math:`Q_{min} = Q_N \cdot \beta/2`
:math:`Q_N = \frac{d^2}{4} \cdot \pi \cdot h \cdot c \cdot \rho \cdot \left( T_{H} - T_{C} \right)` For investment, :math:`Q_N` is not fixed in advance.
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


