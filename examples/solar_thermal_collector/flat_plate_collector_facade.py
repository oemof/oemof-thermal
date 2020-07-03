# -*- coding: utf-8 -*-

"""
Example to show the functionality of the solar thermal collector
with a fixed collector size (aperture area) using the facade.

authors: Franziska Pleissner, Caroline Möller, Marie-Claire Gering

SPDX-License-Identifier: GPL-3.0-or-later
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from oemof.thermal import facades
from oemof import solph
from oemof.tools import economics


# Set paths
base_path = os.path.dirname(os.path.abspath(os.path.join(__file__)))
data_path = os.path.join(base_path, 'data')
results_path = os.path.join(base_path, 'results')
if not os.path.exists(results_path):
    os.mkdir(results_path)

# Parameters for the energy system
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

peripheral_losses = 0.05
elec_consumption = 0.02
backup_costs = 40
costs_storage = economics.annuity(20, 20, 0.06)
costs_electricity = 1000
storage_loss_rate = 0.001
conversion_storage = 0.98
size_collector = 10  # m2

# Read input data
input_data = pd.read_csv(os.path.join(data_path, 'data_flat_collector.csv')).head(periods)
input_data['Datum'] = pd.to_datetime(input_data['Datum'])
input_data.set_index('Datum', inplace=True)
input_data.index = input_data.index.tz_localize(tz='Europe/Berlin')
input_data = input_data.asfreq('H')

demand_df = pd.read_csv(
    os.path.join(data_path, 'heat_demand.csv'),
    sep=','
)
demand = list(demand_df['heat_demand'].iloc[:periods])


# Set up an energy system model

# Busses
bth = solph.Bus(label='thermal')
bel = solph.Bus(label='electricity')

# Collector
collector = facades.SolarThermalCollector(
    label='solar_collector',
    heat_out_bus=bth,
    electricity_in_bus=bel,
    electrical_consumption=elec_consumption,
    peripheral_losses=peripheral_losses,
    aperture_area=size_collector,
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
    temp_amb=input_data['temp_amb'])

# Sources and sinks
el_grid = solph.Source(
    label='grid', outputs={bel: solph.Flow(variable_costs=costs_electricity)}
)

backup = solph.Source(
    label='backup', outputs={bth: solph.Flow(variable_costs=backup_costs)}
)

consumer = solph.Sink(
    label='demand',
    inputs={bth: solph.Flow(fix=demand, nominal_value=1)},
)

collector_excess_heat = solph.Sink(
    label='collector_excess_heat', inputs={bth: solph.Flow()}
)

# Storage
storage = solph.components.GenericStorage(
    label='storage',
    inputs={bth: solph.Flow()},
    outputs={bth: solph.Flow()},
    loss_rate=storage_loss_rate,
    inflow_conversion_factor=conversion_storage,
    outflow_conversion_factor=conversion_storage,
    investment=solph.Investment(ep_costs=costs_storage),
)

# Build the system and solve the problem
date_time_index = input_data.index
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

# Create and solve the optimization model
model = solph.Model(energysystem)
model.solve(solver='cbc', solve_kwargs={'tee': True})

# Get results
results = solph.processing.results(model)

collector_inflow = solph.views.node(
    results, 'solar_collector-inflow')['sequences']
thermal_bus = solph.views.node(results, 'thermal')['sequences']
electricity_bus = solph.views.node(results, 'electricity')['sequences']
df = pd.DataFrame()
df = df.append(collector_inflow)
df = df.join(thermal_bus, lsuffix='_1')
df = df.join(electricity_bus, lsuffix='_1')
df.to_csv(os.path.join(results_path, 'facade_results.csv'))

# Example plot
heat_calc = collector_inflow
t = list(range(1, periods + 1))

fig, ax = plt.subplots()
ax.plot(t, heat_calc)
ax.set(
    xlabel='time in h',
    ylabel='Q_coll in W',
    title='Heat of the collector')
ax.grid()
plt.show()
