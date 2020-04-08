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

from oemof.thermal.solar_thermal_collector import flat_plate_precalc
from oemof.energy_system import EnergySystem
from oemof.network import Node, Transformer, Source
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


class Collector(Transformer, Facade):       # todo: Solve naming conflict (cf. csp)
    r""" Solar thermal collector unit
    Examples:
    ----------
    >>> from oemof import solph
    >>> from oemof.thermal.facades import Collector
    >>> bth = solph.Bus(label='thermal_bus')
    >>> bel = solph.Bus(label='electrical_bus')
    >>> collector = Collector(
    ...     label='solar_collector',
    ...     output_bus=bth, #*
    ...     electrical_bus=bel, #*
    ...     electrical_consumption=0.02, #*
    ...     peripheral_losses=0.05, #*
    ...     dataframe=pd.read_csv(
    ...     os.path.join(base_path, 'data', 'data_flat_collector.csv'),
    ...     sep=';',
    ...     ), # todo How to implement the dataframe here??
    ...     periods=48, #*
    ...     #aperture_area=1000, # todo: Check if can be deleted
    ...     #loss_method='Janotte', # todo: Check if can be deleted
    ...     #irradiance_method='horizontal', # todo: Check if can be deleted
    ...     latitude=52.2443, #*
    ...     longitude=10.5594, #*
    ...     timezone='Europe/Berlin', #*
    ...     collector_tilt=10, #*
    ...     collector_azimuth=20, #*
    ...     #x=0.9, # todo: Check if can be deleted
    ...     eta_0=0.73, #*
    ...     a_1=1.7, #*
    ...     a_2=0.016, #*
    ...     temp_collector_inlet=20, #*
    ...     delta_temp_n=10, #*
    ...     #temp_collector_outlet=500, # todo: Check if can be deleted
    ...     date_col='hour',
    ...     irradiance_global_col='global_horizontal_W_m2',
    ...     irradiance_diffuse_col='diffuse_horizontal_W_m2',
    ...     temp_amb_col='temp_amb',
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

        self.output_bus = kwargs.get("output_bus")

        self.electrical_bus = kwargs.get("electrical_bus")

        self.periods = kwargs.get("periods")

        self.electrical_consumption = kwargs.get("electrical_consumption")

        self.peripheral_losses = kwargs.get("peripheral_losses") # todo: Check if can be deleted

        self.latitude = kwargs.get("latitude")

        self.longitude = kwargs.get("longitude")

        self.collector_tilt = kwargs.get("collector_tilt")

        self.collector_azimuth = kwargs.get("collector_azimuth")

        self.a_1 = kwargs.get("a_1")

        self.a_2 = kwargs.get("a_2")

        self.eta_0 = kwargs.get("eta_0")

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
        self.conversion_factors=\
            {
                self.electrical_bus: sequence(self.electrical_consumption),
                self.output_bus: sequence(1-self.peripheral_losses),
            }

        if self.expandable:
            raise NotImplementedError(
                "Investment for reservoir class is not implemented."
            )

        inflow = Source(    # todo: Adjust !
            label=self.label + "-inflow",
            outputs={
                self: Flow(nominal_value=self.aperture_area,
                           actual_value=self.collectors_heat,
                           fixed=True)
            },
        )

        self.inputs.update(
            {
                self.electrical_bus: Flow(
                )
            }
        )
        self.outputs.update(
            {
                self.output_bus: Flow(
                )
            }
        )

        self.subnodes = (inflow,)
