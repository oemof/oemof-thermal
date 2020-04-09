# -*- coding: utf-8 -*-

"""
Example to show the functionality of the solar thermal collector
with a collector size (aperture area) to be invested.

authors: Franziska Pleissner, Caroline Möller

SPDX-License-Identifier: GPL-3.0-or-later
"""
import os

import pandas as pd

from oemof import solph
from oemof.tools import economics
from oemof.thermal.solar_thermal_collector import flat_plate_precalc
import oemof.outputlib as outputlib
from plots import plot_collector_heat


# set paths
base_path = os.path.dirname(os.path.abspath(os.path.join(__file__)))
data_path = os.path.join(base_path, 'data/')
results_path = os.path.join(base_path, 'results/')
if not os.path.exists(results_path):
    os.mkdir(results_path)

# parameters for the precalculation
periods = 48
latitude = 52.2443
longitude = 10.5594
collector_tilt = 10
collector_azimuth = 20
eta_0 = 0.73
a_1 = 1.7
a_2 = 0.016
temp_collector_inlet = 20
delta_temp_n = 10

# input data
input_data = pd.read_csv(data_path + 'data_flat_collector.csv').head(periods)
input_data['hour'] = pd.to_datetime(input_data['hour'])
input_data.set_index('hour', inplace=True)
input_data.index = input_data.index.tz_localize(tz='Europe/Berlin')

demand_df = pd.read_csv(
    os.path.join(base_path, 'data', 'heat_demand.csv'),
    sep=','
)
demand = list(demand_df['heat_demand'].iloc[:periods])

# precalculation
# - calculate global irradiance on the collector area
# and collector efficiency depending on the
# temperature difference -
precalc_data = flat_plate_precalc(
    latitude,
    longitude,
    collector_tilt,
    collector_azimuth,
    eta_0,
    a_1,
    a_2,
    temp_collector_inlet,
    delta_temp_n,
    irradiance_global=input_data['global_horizontal_W_m2'],
    irradiance_diffuse=input_data['diffuse_horizontal_W_m2'],
    temp_amb=input_data['temp_amb'],
)

precalc_data.to_csv(
    os.path.join(results_path, 'flate_plate_precalcs.csv'),
    sep=';'
)


# regular oemof system #

# parameters for the energy system
eta_losses = 0.05
elec_consumption = 0.02
backup_costs = 40
costs_collector = economics.annuity(20, 20, 0.06)
costs_storage = economics.annuity(20, 20, 0.06)
costs_electricity = 1000
storage_loss_rate = 0.001
conversion_storage = 0.98

# busses
bth = solph.Bus(label='thermal', balanced=True)
bel = solph.Bus(label='electricity')
bcol = solph.Bus(label='solar')

# source for collector heat.
# - actual_value is the precalculated collector heat -
collector_heat = solph.Source(
    label='collector_heat',
    outputs={
        bcol: solph.Flow(
            fixed=True,
            actual_value=precalc_data['collectors_heat'],
            investment=solph.Investment(ep_costs=costs_collector),
        )
    },
)

# sources and sinks
el_grid = solph.Source(
    label='grid', outputs={bel: solph.Flow(variable_costs=costs_electricity)}
)

backup = solph.Source(
    label='backup', outputs={bth: solph.Flow(variable_costs=backup_costs)}
)

consumer = solph.Sink(
    label='demand',
    inputs={bth: solph.Flow(fixed=True, actual_value=demand, nominal_value=1)},
)

collector_excess_heat = solph.Sink(
    label='collector_excess_heat', inputs={bcol: solph.Flow()}
)

# transformer and storage
collector = solph.Transformer(
    label='collector',
    inputs={bcol: solph.Flow(), bel: solph.Flow()},
    outputs={bth: solph.Flow()},
    conversion_factors={
        bcol: 1 - elec_consumption,
        bel: elec_consumption,
        bth: 1 - eta_losses,
    },
)

storage = solph.components.GenericStorage(
    label='storage',
    inputs={bth: solph.Flow()},
    outputs={bth: solph.Flow()},
    loss_rate=storage_loss_rate,
    inflow_conversion_factor=conversion_storage,
    outflow_conversion_factor=conversion_storage,
    investment=solph.Investment(ep_costs=costs_storage),
)

# build the system and solve the problem
date_time_index = input_data.index
energysystem = solph.EnergySystem(timeindex=date_time_index)

energysystem.add(
    bth,
    bcol,
    bel,
    collector_heat,
    el_grid,
    backup,
    consumer,
    collector_excess_heat,
    storage,
    collector,
)

model = solph.Model(energysystem)
model.solve(solver='cbc', solve_kwargs={'tee': True})

model.write('solar_thermal_collector_model.lp', io_options={'symbolic_solver_labels': True})

energysystem.results['main'] = outputlib.processing.results(model)
energysystem.results['meta'] = outputlib.processing.meta_results(model)

collector = outputlib.views.node(energysystem.results['main'], 'collector')
thermal_bus = outputlib.views.node(energysystem.results['main'], 'thermal')
df = pd.DataFrame()
df = df.append(collector['sequences'])
df = df.join(thermal_bus['sequences'], lsuffix='_1')
df.to_csv(
    os.path.join(results_path, 'thermal_bus_flat_plate.csv'),
    sep=';',
)

# Example plot
plot_collector_heat(precalc_data, periods, eta_0)
