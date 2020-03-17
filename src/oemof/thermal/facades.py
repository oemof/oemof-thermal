# -*- coding: utf-8 -*-

"""
Adapted from `oemof.tabular's facades
<https://github.com/oemof/oemof-tabular/blob/master/src/oemof/tabular/facades.py>`_

Facade's are classes providing a simplified view on more complex classes.
More specifically, the `Facade`s in this module act as simplified, energy
specific  wrappers around `oemof`'s and `oemof.solph`'s more abstract and
complex classes. The idea is to be able to instantiate a `Facade` using keyword
arguments, whose value are derived from simple, tabular data sources. Under the
hood the `Facade` then uses these arguments to construct an `oemof` or
`oemof.solph` component and sets it up to be easily used in an `EnergySystem`.
**Note** The mathematical notation is as follows:
* Optimization variables (endogenous) are denoted by :math:`x`
* Optimization parameters (exogenous) are denoted by :math:`c`
* The set of timesteps :math:`T` describes all timesteps of the optimization
  problem
SPDX-License-Identifier:
"""

from collections import deque

from oemof.thermal.stratified_thermal_storage import calculate_storage_dimensions,\
    calculate_capacities, calculate_losses
from oemof.energy_system import EnergySystem
from oemof.network import Node
from oemof.solph import Flow, Investment
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
    r""" Stratified thermal storage unit

    Parameters
    ----------
    bus: oemof.solph.Bus
        An oemof bus instance where the storage unit is connected to.
    storage_capacity: numeric
        The total capacity of the storage (e.g. in MWh)
    capacity: numeric
        Maximum production capacity (e.g. in MW)
    efficiency: numeric
        Efficiency of charging and discharging process: Default: 1
    storage_capacity_cost: numeric
        Investment costs for the storage unit e.g in €/MWh-capacity
    expandable: boolean
        True, if capacity can be expanded within optimization. Default: False.
    storage_capacity_potential: numeric
        Potential of the investment for storage capacity in MWh
    capacity_potential: numeric
        Potential of the investment for capacity in MW
    input_parameters: dict (optional)
        Set parameters on the input edge of the storage (see oemof.solph for
        more information on possible parameters)
    ouput_parameters: dict (optional)
        Set parameters on the output edge of the storage (see oemof.solph for
        more information on possible parameters)
    Intertemporal energy balance of the storage:
    .. math::
        x^{level}(t) =
        x^{level}(t-1) \cdot (1 - c^{loss\_rate})
        + \sqrt{c^{efficiency}(t)}  x^{flow, in}(t)
        - \frac{x^{flow, out}(t)}{\sqrt{c^{efficiency}(t)}}
        \qquad \forall t \in T
    .. math::
        x^{level}(0) = 0.5 \cdot c^{capacity}
    The **expression** added to the cost minimizing objective funtion
    for the operation is given as:
    .. math::
        x^{opex} = \sum_t (x^{flow, out}(t) \cdot c^{marginal\_cost}(t))

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

        self.diameter = kwargs.get("diameter")

        self.height = kwargs.get("height")

        self.temp_h = kwargs.get("temp_h")

        self.temp_c = kwargs.get("temp_c")

        self.temp_env = kwargs.get("temp_env")

        self.u_value = kwargs.get("u_value")

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
                0,
                **{key: value for key, value in self.water_properties.items() if value is not None}
            )[0]

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
