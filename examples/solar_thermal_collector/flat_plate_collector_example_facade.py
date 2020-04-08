# -*- coding: utf-8 -*-

"""Solar thermal collectors

authors:

SPDX-License-Identifier: GPL-3.0-or-later
"""
import os
import pandas as pd
import oemof.outputlib as outputlib

from oemof.thermal import facades
from oemof import solph
from oemof.tools import economics


# set paths
base_path = os.path.dirname(os.path.abspath(os.path.join(__file__)))

results_path = os.path.join(base_path, 'results/')
lp_path = os.path.join(base_path, 'lp_files/')
data_path = os.path.join(base_path, 'data/')

if not os.path.exists(results_path):
        os.mkdir(results_path)


# Set up an energy system model
periods = 48
latitude = 52.2443
longitude = 10.5594
collector_tilt = 10
collector_azimuth = 20
a_1 = 1.7
a_2 = 0.016
eta_0 = 0.73
temp_collector_inlet = 20
delta_temp_n = 10

input_data = pd.read_csv(data_path + 'data_flat_collector_2.csv').head(periods)
print(input_data)
input_data['hour'] = pd.to_datetime(input_data['hour'])
input_data.set_index('hour', inplace=True)
input_data.index = input_data.index.tz_localize(tz='Europe/Berlin')

date_time_index = input_data.index

# Read demand time series from csv file
demand_df = pd.read_csv(
    os.path.join(base_path, 'data', 'heat_demand.csv'),
    sep=','
)
demand = list(demand_df['heat_demand'].iloc[:periods])

# Define parameters for the energy system
eta_losses = 0.05
elec_consumption = 0.02
backup_costs = 40
costs_collector = economics.annuity(20, 20, 0.06)
costs_storage = economics.annuity(20, 20, 0.06)
costs_electricity = 1000
storage_loss_rate = 0.001
conversion_storage = 0.98

# busses
bth = solph.Bus(label='thermal')
bel = solph.Bus(label='electricity')

collector = facades.SolarThermalCollector(
    label='solar_collector',
    output_bus=bth,
    electrical_bus=bel,
    periods=periods,
    electrical_consumption=elec_consumption,
    peripheral_losses=eta_losses,
    latitude=latitude,
    longitude=longitude,
    collector_tilt=collector_tilt,
    collector_azimuth=collector_azimuth,
    eta_0=eta_0,
    a_1=a_1,
    a_2=a_2,
    temp_collector_inlet=temp_collector_inlet,
    delta_temp_n=delta_temp_n,
    irradiance_global=input_data['global_horizontal_W_m2'],
    irradiance_diffuse=input_data['diffuse_horizontal_W_m2'],
    temp_amb=input_data['temp_amb'],
    )

# Create source for electricity grid.
el_grid = solph.Source(
    label='grid', outputs={bel: solph.Flow(variable_costs=costs_electricity)}
)

# Create source for backup heat supply.
backup = solph.Source(
    label='backup', outputs={bth: solph.Flow(variable_costs=backup_costs)}
)

# Create sink for heat demand.
consumer = solph.Sink(
    label='demand',
    inputs={bth: solph.Flow(fixed=True, actual_value=demand, nominal_value=1)},
)

# Create sink for collector excess heat.
collector_excess_heat = solph.Sink(
    label='collector_excess_heat', inputs={bth: solph.Flow()}
)

# Create heat storage.
storage = solph.components.GenericStorage(
    label='storage',
    inputs={bth: solph.Flow()},
    outputs={bth: solph.Flow()},
    loss_rate=storage_loss_rate,
    inflow_conversion_factor=conversion_storage,
    outflow_conversion_factor=conversion_storage,
    investment=solph.Investment(ep_costs=costs_storage),
)

energysystem = solph.EnergySystem(timeindex=date_time_index)

energysystem.add(
    bth,
    bel,
    collector,
    el_grid,
    backup,
    consumer,
    collector_excess_heat,
    storage,
)

model = solph.Model(energysystem)

model.solve(solver='cbc', solve_kwargs={'tee': True})

