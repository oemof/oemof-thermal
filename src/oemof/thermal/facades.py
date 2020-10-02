# -*- coding: utf-8 -*-

"""
Adapted from `oemof.tabular's facades
<https://github.com/oemof/oemof-tabular/blob/master/src/oemof/tabular/facades.py>`_

Facade's are classes providing a simplified view on more complex classes.
More specifically, the :class:`Facade` s in this module inherit from `oemof.solph`'s generic
classes to serve as more concrete and energy specific interface.

The concept of the facades has been derived from oemof.tabular. The idea is to be able to
instantiate a :class:`Facade` using only keyword arguments. Under the hood the :class:`Facade` then
uses these arguments to construct an `oemof.solph` component and sets it up to be easily used in an
:class:`EnergySystem`. Usually, a subset of the attributes of the parent class remains while another
part can be addressed by more specific or simpler attributes.

**Note** The mathematical notation is as follows:

* Optimization variables (endogenous) are denoted by :math:`x`
* Optimization parameters (exogenous) are denoted by :math:`c`
* The set of timesteps :math:`T` describes all timesteps of the optimization
  problem

SPDX-License-Identifier: MIT
"""

from collections import deque

from oemof.thermal.stratified_thermal_storage import calculate_storage_dimensions,\
    calculate_capacities, calculate_losses
from oemof.thermal.concentrating_solar_power import csp_precalc
from oemof.thermal.solar_thermal_collector import flat_plate_precalc
from oemof.network.energy_system import EnergySystem
from oemof.network.network import Node
from oemof.solph import Flow, Investment, Transformer, Source
from oemof.solph.components import GenericStorage
from oemof.solph.plumbing import sequence


def add_subnodes(n, **kwargs):
    deque((kwargs["EnergySystem"].add(sn) for sn in n.subnodes), maxlen=0)


class Facade(Node):
    """
    Parameters
    ----------
    _facade_requires_ : list of str
        A list of required attributes. The constructor checks whether these are
        present as keyword arguments or whether they are already present on
        self (which means they have been set by constructors of subclasses) and
        raises an error if he doesn't find them.
    """

    def __init__(self, *args, **kwargs):
        """
        """

        self.mapped_type = type(self)

        self.type = kwargs.get("type")

        required = kwargs.pop("_facade_requires_", [])

        super().__init__(*args, **kwargs)

        self.subnodes = []
        EnergySystem.signals[EnergySystem.add].connect(
            add_subnodes, sender=self
        )

        for r in required:
            if r in kwargs:
                setattr(self, r, kwargs[r])
            elif not hasattr(self, r):
                raise AttributeError(
                    (
                        "Missing required attribute `{}` for `{}` "
                        "object with name/label `{!r}`."
                    ).format(r, type(self).__name__, self.label)
                )

    def _nominal_value(self):
        """ Returns None if self.expandable ist True otherwise it returns
        the capacity
        """
        if self.expandable is True:
            return None

        else:
            return self.capacity

    def _investment(self):
        if self.expandable is True:
            if self.capacity_cost is None:
                msg = (
                    "If you set `expandable`to True you need to set "
                    "attribute `capacity_cost` of component {}!"
                )
                raise ValueError(msg.format(self.label))
            else:
                if isinstance(self, GenericStorage):
                    if self.storage_capacity_cost is not None:
                        self.investment = Investment(
                            ep_costs=self.storage_capacity_cost,
                            maximum=getattr(
                                self,
                                "storage_capacity_potential",
                                float("+inf"),
                            ),
                            minimum=getattr(
                                self, "minimum_storage_capacity", 0
                            ),
                            existing=getattr(self, "storage_capacity", 0),
                        )
                    else:
                        self.investment = Investment()
                else:
                    self.investment = Investment(
                        ep_costs=self.capacity_cost,
                        maximum=getattr(
                            self, "capacity_potential", float("+inf")
                        ),
                        existing=getattr(self, "capacity", 0),
                    )
        else:
            self.investment = None

        return self.investment

    def update(self):
        self.build_solph_components()


class StratifiedThermalStorage(GenericStorage, Facade):
    r""" Stratified thermal storage unit.

    Parameters
    ----------
    bus: oemof.solph.Bus
        An oemof bus instance where the storage unit is connected to.
    diameter : numeric
        Diameter of the storage [m]
    height : numeric
        Height of the storage [m]
    temp_h : numeric
        Temperature of the hot (upper) part of the water body.
    temp_c : numeric
        Temperature of the cold (upper) part of the water body.
    temp_env : numeric
        Temperature of the environment.
    heat_capacity : numeric
        Assumed constant for heat capacity of the water.
    density : numeric
        Assumed constant for density of the water.
    u_value : numeric
        Thermal transmittance [W/(m2*K)]
    capacity: numeric
        Maximum production capacity [MW]
    efficiency: numeric
        Efficiency of charging and discharging process: Default: 1
    marginal_cost: numeric
        Marginal cost for one unit of output.
    expandable: boolean
        True, if capacity can be expanded within optimization. Default: False.
    storage_capacity_cost: numeric
        Investment costs for the storage unit [Eur/MWh].
    capacity_cost : numeric
        Investment costs for charging/dischargin [Eur/MW]
    storage_capacity_potential: numeric
        Potential of the investment for storage capacity [MWh]
    capacity_potential: numeric
        Potential of the investment for capacity [MW]
    input_parameters: dict (optional)
        Set parameters on the input edge of the storage (see oemof.solph for
        more information on possible parameters)
    output_parameters: dict (optional)
        Set parameters on the output edge of the storage (see oemof.solph for
        more information on possible parameters)


    The attribute :attr:`nominal_storage_capacity` of the base class :class:`GenericStorage`
    should not be passed because it is determined internally from :attr:`height`
    and :attr:`parameter`.

    Examples
    ---------
    >>> from oemof import solph
    >>> from oemof.thermal.facades import StratifiedThermalStorage
    >>> heat_bus = solph.Bus(label='heat_bus')
    >>> thermal_storage = StratifiedThermalStorage(
    ...     label='thermal_storage',
    ...     bus=heat_bus,
    ...     diameter=10,
    ...     height=10,
    ...     temp_h=95,
    ...     temp_c=60,
    ...     temp_env=10,
    ...     u_value=0.3,
    ...     initial_storage_level=0.5,
    ...     min_storage_level=0.05,
    ...     max_storage_level=0.95
    ...     capacity=1)
    """

    def __init__(self, *args, **kwargs):

        super().__init__(
            _facade_requires_=[
                "bus", "diameter",
                "temp_h", "temp_c", "temp_env",
                "u_value"], *args, **kwargs
        )

        self.height = kwargs.get("height")

        self.water_properties = {
            'heat_capacity': kwargs.get("heat_capacity"), 'density': kwargs.get("density")
        }

        self.capacity = kwargs.get("capacity")

        self.storage_capacity_cost = kwargs.get("storage_capacity_cost")

        self.capacity_cost = kwargs.get("capacity_cost")

        self.storage_capacity_potential = kwargs.get(
            "storage_capacity_potential", float("+inf")
        )

        self.capacity_potential = kwargs.get(
            "capacity_potential", float("+inf")
        )

        self.minimum_storage_capacity = kwargs.get(
            "minimum_storage_capacity", 0
        )

        self.expandable = bool(kwargs.get("expandable", False))

        if self.expandable and self.capacity is None:
            self.capacity = 0

        self.efficiency = kwargs.get("efficiency", 1)

        self.marginal_cost = kwargs.get("marginal_cost", 0)

        self.input_parameters = kwargs.get("input_parameters", {})

        self.output_parameters = kwargs.get("output_parameters", {})

        losses = calculate_losses(
            self.u_value,
            self.diameter,
            self.temp_h,
            self.temp_c,
            self.temp_env,
            **{key: value for key, value in self.water_properties.items() if value is not None}
        )

        self.loss_rate = losses[0]

        self.fixed_losses_relative = losses[1]

        self.fixed_losses_absolute = losses[2]

        self.build_solph_components()

    def build_solph_components(self):
        """
        """
        self.inflow_conversion_factor = sequence(self.efficiency)

        self.outflow_conversion_factor = sequence(self.efficiency)

        self.loss_rate = sequence(self.loss_rate)

        self.fixed_losses_relative = sequence(self.fixed_losses_relative)

        self.fixed_losses_absolute = sequence(self.fixed_losses_absolute)

        # make it investment but don't set costs (set below for flow (power))
        self.investment = self._investment()

        if self.investment:
            self.invest_relation_input_output = 1

            for attr in ["invest_relation_input_output"]:
                if getattr(self, attr) is None:
                    raise AttributeError(
                        (
                            "You need to set attr " "`{}` " "for component {}"
                        ).format(attr, self.label)
                    )

            # set capacity costs at one of the flows
            fi = Flow(
                investment=Investment(
                    ep_costs=self.capacity_cost,
                    maximum=self.capacity_potential,
                    existing=self.capacity,
                ),
                **self.input_parameters
            )
            # set investment, but no costs (as relation input / output = 1)
            fo = Flow(
                investment=Investment(),
                variable_costs=self.marginal_cost,
                **self.output_parameters
            )
            # required for correct grouping in oemof.solph.components
            self._invest_group = True
        else:
            self.volume = calculate_storage_dimensions(self.height, self.diameter)[0]

            self.nominal_storage_capacity = calculate_capacities(
                self.volume,
                self.temp_h,
                self.temp_c,
                **{key: value for key, value in self.water_properties.items() if value is not None}
            )

            fi = Flow(
                nominal_value=self._nominal_value(), **self.input_parameters
            )
            fo = Flow(
                nominal_value=self._nominal_value(),
                variable_costs=self.marginal_cost,
                **self.output_parameters
            )

        self.inputs.update({self.bus: fi})

        self.outputs.update({self.bus: fo})

        self._set_flows()


class ParabolicTroughCollector(Transformer, Facade):
    r""" Parabolic trough collector unit

    Parameters
    ----------
    heat_bus: oemof.solph.Bus
        An oemof bus instance in which absorbs the collectors heat.
    electrical_bus: oemof.solph.Bus
        An oemof bus instance which provides electrical energy to the collector.
    electrical_consumption: numeric
        Specifies how much electrical energy is used per provided thermal energy.
    additional_losses: numeric
        Specifies how much thermal energy is lost in peripheral parts like
        pipes and pumps.
    aperture_area: numeric
        Specify the ares or size of the collector.


    See the API of csp_precalc in oemof.thermal.concentrating_solar_power for
    the other parameters.

    Examples
    --------
    >>> from oemof import solph
    >>> from oemof.thermal.facades import ParabolicTroughCollector
    >>> bth = solph.Bus(label='thermal_bus')
    >>> bel = solph.Bus(label='electrical_bus')
    >>> collector = ParabolicTroughCollector(
    ...     label='solar_collector',
    ...     heat_bus=bth,
    ...     electrical_bus=bel,
    ...     electrical_consumption=0.05,
    ...     additional_losses=0.2,
    ...     aperture_area=1000,
    ...     loss_method='Janotte',
    ...     irradiance_method='horizontal',
    ...     latitude=23.614328,
    ...     longitude=58.545284,
    ...     collector_tilt=10,
    ...     collector_azimuth=180,
    ...     x=0.9,
    ...     a_1=-0.00159,
    ...     a_2=0.0000977,
    ...     eta_0=0.816,
    ...     c_1=0.0622,
    ...     c_2=0.00023,
    ...     temp_collector_inlet=435,
    ...     temp_collector_outlet=500,
    ...     temp_amb=input_data['t_amb'],
    ...     irradiance=input_data['E_dir_hor']
    ... )
    """

    def __init__(self, *args, **kwargs):

        kwargs.update(
            {
                "_facade_requires_": [
                    "longitude"
                ]
            }
        )
        super().__init__(*args, **kwargs)

        self.label = kwargs.get("label")

        self.heat_bus = kwargs.get("heat_bus")

        self.electrical_bus = kwargs.get("electrical_bus")

        self.electrical_consumption = kwargs.get("electrical_consumption")

        self.additional_losses = kwargs.get("additional_losses")

        self.aperture_area = kwargs.get("aperture_area")

        self.latitude = kwargs.get("latitude")

        self.longitude = kwargs.get("longitude")

        self.collector_tilt = kwargs.get("collector_tilt")

        self.collector_azimuth = kwargs.get("collector_azimuth")

        self.cleanliness = kwargs.get("cleanliness")

        self.eta_0 = kwargs.get("eta_0")

        self.c_1 = kwargs.get("c_1")

        self.c_2 = kwargs.get("c_2")

        self.a_1 = kwargs.get("a_1")

        self.a_2 = kwargs.get("a_2")

        self.a_3 = kwargs.get("a_3", 0)

        self.a_4 = kwargs.get("a_4", 0)

        self.a_5 = kwargs.get("a_5", 0)

        self.a_6 = kwargs.get("a_6", 0)

        self.temp_collector_inlet = kwargs.get("temp_collector_inlet")

        self.temp_collector_outlet = kwargs.get("temp_collector_outlet")

        self.temp_amb = kwargs.get("temp_amb")

        self.loss_method = kwargs.get("loss_method")

        self.irradiance_method = kwargs.get("irradiance_method")

        self.irradiance = kwargs.get("irradiance")

        self.expandable = bool(kwargs.get("expandable", False))

        if self.irradiance_method == "horizontal":
            heat = csp_precalc(
                self.latitude, self.longitude,
                self.collector_tilt, self.collector_azimuth, self.cleanliness,
                self.eta_0, self.c_1, self.c_2,
                self.temp_collector_inlet, self.temp_collector_outlet,
                self.temp_amb,
                self.a_1, self.a_2, self.a_3, self.a_4, self.a_5, self.a_6,
                loss_method=self.loss_method,
                irradiance_method=self.irradiance_method,
                E_dir_hor=self.irradiance
            )
        if self.irradiance_method == "normal":
            heat = csp_precalc(
                self.latitude, self.longitude,
                self.collector_tilt, self.collector_azimuth, self.cleanliness,
                self.eta_0, self.c_1, self.c_2,
                self.temp_collector_inlet, self.temp_collector_outlet,
                self.temp_amb,
                self.a_1, self.a_2, self.a_3, self.a_4, self.a_5, self.a_6,
                loss_method=self.loss_method,
                irradiance_method=self.irradiance_method,
                dni=self.irradiance
            )

        self.collectors_heat = heat['collector_heat']

        self.build_solph_components()

    def build_solph_components(self):
        """
        """

        if self.expandable:
            raise NotImplementedError(
                "Investment for reservoir class is not implemented."
            )

        inflow = Source(
            label=self.label + "-inflow",
            outputs={
                self: Flow(nominal_value=self.aperture_area,
                           max=self.collectors_heat)
            },
        )

        self.conversion_factors.update(
            {
                self.electrical_bus: sequence(self.electrical_consumption
                                              * (1 - self.additional_losses)),
                self.heat_bus: sequence(1 - self.additional_losses),
                inflow: sequence(1)
            }
        )

        self.inputs.update(
            {self.electrical_bus: Flow()}
        )
        self.outputs.update(
            {self.heat_bus: Flow()}
        )

        self.subnodes = (inflow,)


class SolarThermalCollector(Transformer, Facade):
    r""" Solar thermal collector unit

    Parameters:
    -----------
    heat_out_bus: oemof.solph.Bus
        An oemof bus instance which absorbs the collectors heat.
    electrical_in_bus: oemof.solph.Bus
        An oemof bus instance which provides electrical energy to the collector.
    electrical_consumption: numeric
        Specifies how much electrical energy is used per provided thermal energy.
    peripheral_losses: numeric
        Specifies how much thermal energy is lost in peripheral parts like
        pipes and pumps as percentage of provided thermal energy.
    aperture_area: numeric
        Specifies the size of the collector as surface area.

    See the API of flat_plate_precalc in oemof.thermal.solar_thermal_collector for
    the other parameters.

    Example:
    ----------
    >>> from oemof import solph
    >>> from oemof.thermal.facades import SolarThermalCollector
    >>> bth = solph.Bus(label='thermal')
    >>> bel = solph.Bus(label='electricity')
    >>> collector = SolarThermalCollector(
    ...     label='solar_collector',
    ...     heat_out_bus=bth,
    ...     electricity_in_bus=bel,
    ...     electrical_consumption=0.02,
    ...     peripheral_losses=0.05,
    ...     aperture_area=1000,
    ...     latitude=52.2443,
    ...     longitude=10.5594,
    ...     collector_tilt=10,
    ...     collector_azimuth=20,
    ...     eta_0=0.73,
    ...     a_1=1.7,
    ...     a_2=0.016,
    ...     temp_collector_inlet=20,
    ...     delta_temp_n=10,
    ...     irradiance_global=input_data['global_horizontal_W_m2'],
    ...     irradiance_diffuse=input_data['diffuse_horizontal_W_m2'],
    ...     temp_amb=input_data['temp_amb'],
    )
    """

    def __init__(self, *args, **kwargs):

        kwargs.update(
            {
                "_facade_requires_": [
                    "longitude"
                ]
            }
        )
        super().__init__(*args, **kwargs)

        self.label = kwargs.get("label")

        self.heat_out_bus = kwargs.get("heat_out_bus")

        self.electricity_in_bus = kwargs.get("electricity_in_bus")

        self.electrical_consumption = kwargs.get("electrical_consumption")

        self.peripheral_losses = kwargs.get("peripheral_losses")

        self.aperture_area = kwargs.get("aperture_area")

        self.latitude = kwargs.get("latitude")

        self.longitude = kwargs.get("longitude")

        self.collector_tilt = kwargs.get("collector_tilt")

        self.collector_azimuth = kwargs.get("collector_azimuth")

        self.eta_0 = kwargs.get("eta_0")

        self.a_1 = kwargs.get("a_1")

        self.a_2 = kwargs.get("a_2")

        self.temp_collector_inlet = kwargs.get("temp_collector_inlet")

        self.delta_temp_n = kwargs.get("delta_temp_n")

        self.irradiance_global = kwargs.get("irradiance_global")

        self.irradiance_diffuse = kwargs.get("irradiance_diffuse")

        self.temp_amb = kwargs.get("temp_amb")

        self.expandable = bool(kwargs.get("expandable", False))

        data = flat_plate_precalc(
            self.latitude,
            self.longitude,
            self.collector_tilt,
            self.collector_azimuth,
            self.eta_0,
            self.a_1,
            self.a_2,
            self.temp_collector_inlet,
            self.delta_temp_n,
            self.irradiance_global,
            self.irradiance_diffuse,
            self.temp_amb,
        )

        self.collectors_eta_c = data['eta_c']

        self.collectors_heat = data['collectors_heat']

        self.build_solph_components()

    def build_solph_components(self):
        """
        """

        if self.expandable:
            raise NotImplementedError(
                "Investment for solar thermal collector facade has not been implemented yet."
            )

        inflow = Source(
            label=self.label + "-inflow",
            outputs={
                self: Flow(nominal_value=self.aperture_area,
                           max=self.collectors_heat)
            },
        )

        self.conversion_factors.update(
            {
                self.electricity_in_bus: sequence(self.electrical_consumption
                                                  * (1 - self.peripheral_losses)),
                self.heat_out_bus: sequence(1 - self.peripheral_losses),
                inflow: sequence(1)
            }
        )

        self.inputs.update(
            {
                self.electricity_in_bus: Flow(
                )
            }
        )
        self.outputs.update(
            {
                self.heat_out_bus: Flow(
                )
            }
        )

        self.subnodes = (inflow,)
