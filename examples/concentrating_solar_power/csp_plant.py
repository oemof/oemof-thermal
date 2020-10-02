# -*- coding: utf-8 -*-
"""
Example to show the functionality of the concentrating solar thermal collector

authors: Franziska Pleissner

SPDX-License-Identifier: GPL-3.0-or-later
"""
import os

import pandas as pd

from oemof import solph
from oemof.tools import economics
from oemof.thermal.concentrating_solar_power import csp_precalc

import matplotlib.pyplot as plt

# Set paths
base_path = os.path.dirname(os.path.abspath(os.path.join(__file__)))

results_path = os.path.join(base_path, 'results')
data_path = os.path.join(base_path, 'data')

if not os.path.exists(results_path):
    os.mkdir(results_path)

# Parameters for the precalculation
periods = 50
latitude = 23.614328
longitude = 58.545284
collector_tilt = 10
collector_azimuth = 180
cleanliness = 0.9
a_1 = -0.00159
a_2 = 0.0000977
eta_0 = 0.816
c_1 = 0.0622
c_2 = 0.00023
temp_collector_inlet = 435
temp_collector_outlet = 500

# Read and preprocess input data

# It is necessary, to set a timeindex, so the pvlib is able to process the data
# Here, the given column 'Datum' is convertet to a datetime and this is used as
# index:
dataframe = pd.read_csv(os.path.join(data_path, 'data_csp_plant.csv')).head(periods)
dataframe['Datum'] = pd.to_datetime(dataframe['Datum'])
dataframe.set_index('Datum', inplace=True)
# For some pandas version, it is necessary to set the frequence of the df:
dataframe = dataframe.asfreq('H')
# The time of the input data is given locally, so it has to be adapted to the
# correct timezone:
dataframe.index = dataframe.index.tz_localize(tz='Asia/Muscat')

# Precalculation
data_precalc = csp_precalc(latitude, longitude,
                           collector_tilt, collector_azimuth, cleanliness,
                           eta_0, c_1, c_2,
                           temp_collector_inlet, temp_collector_outlet,
                           dataframe['t_amb'],
                           a_1, a_2,
                           E_dir_hor=dataframe['E_dir_hor'])

data_precalc['ES_load_actual_entsoe_power_statistics'] = list(
    dataframe['ES_load_actual_entsoe_power_statistics'].iloc[:periods])

data_precalc.to_csv(os.path.join(results_path, 'results_csp_plant_precalc.csv'))

# Regular oemof_system

# Parameters for the energy system
additional_losses = 0.2
elec_consumption = 0.05
backup_costs = 1000
cap_loss = 0.02
conversion_storage = 0.95
costs_storage = economics.annuity(20, 20, 0.06)
costs_electricity = 1000
conversion_factor_turbine = 0.4
size_collector = 1000

# Busses
bth = solph.Bus(label='thermal')
bel = solph.Bus(label='electricity')
bcol = solph.Bus(label='solar')

# Sources and sinks
col_heat = solph.Source(
    label='collector_heat',
    outputs={bcol: solph.Flow(
        fix=data_precalc['collector_heat'],
        nominal_value=size_collector)})

el_grid = solph.Source(
    label='grid',
    outputs={bel: solph.Flow(variable_costs=costs_electricity)})

backup = solph.Source(
    label='backup',
    outputs={bth: solph.Flow(variable_costs=backup_costs)})

consumer = solph.Sink(
    label='demand',
    inputs={bel: solph.Flow(
        fix=data_precalc['ES_load_actual_entsoe_power_statistics'],
        nominal_value=1)})

ambience_sol = solph.Sink(
    label='ambience_sol',
    inputs={bcol: solph.Flow()})

# Transformer and storages
collector = solph.Transformer(
    label='collector',
    inputs={
        bcol: solph.Flow(),
        bel: solph.Flow()},
    outputs={bth: solph.Flow()},
    conversion_factors={
        bcol: 1,
        bel: elec_consumption * (1 - additional_losses),
        bth: 1 - additional_losses})

turbine = solph.Transformer(
    label='turbine',
    inputs={bth: solph.Flow()},
    outputs={bel: solph.Flow()},
    conversion_factors={bel: conversion_factor_turbine})

storage = solph.components.GenericStorage(
    label='storage_th',
    inputs={bth: solph.Flow()},
    outputs={bth: solph.Flow()},
    loss_rate=cap_loss,
    inflow_conversion_factor=conversion_storage,
    outflow_conversion_factor=conversion_storage,
    investment=solph.Investment(ep_costs=costs_storage))

# Build the system and solve the problem
date_time_index = dataframe.index
energysystem = solph.EnergySystem(timeindex=date_time_index)

energysystem.add(bth, bcol, bel, col_heat, el_grid, backup, consumer,
                 ambience_sol, collector, turbine, storage)

# Create and solve the optimization model
model = solph.Model(energysystem)
model.solve(solver='cbc', solve_kwargs={'tee': True})

# Get results
results = solph.processing.results(model)

electricity_bus = solph.views.node(results, 'electricity')['sequences']
thermal_bus = solph.views.node(results, 'thermal')['sequences']
solar_bus = solph.views.node(results, 'solar')['sequences']
df = pd.merge(
    pd.merge(electricity_bus, thermal_bus, left_index=True, right_index=True),
    solar_bus, left_index=True, right_index=True)
df.to_csv(os.path.join(results_path, 'csp_plant_results.csv'))

# Example plot
fig, ax = plt.subplots()
ax.plot(list(range(periods)), thermal_bus[(('collector', 'thermal'), 'flow')])
ax.set(xlabel='time [h]', ylabel='Q_coll [W]',
       title='Heat of the collector')
ax.grid()
plt.show()
