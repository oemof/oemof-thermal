# -*- coding: utf-8 -*-

"""Solar thermal collectors

authors:

SPDX-License-Identifier: GPL-3.0-or-later
"""

from oemof import solph
from oemof.tools import economics
from oemof.thermal.CSP import csp_precalc
import pandas as pd
import os
import oemof.outputlib as outputlib

# precaluculation #

# path = os.path.dirname(os.path.abspath(os.path.join(__file__, '..', '..')))
dataframe = pd.read_csv('CSP_data/data_CSP.csv', sep=';')
dataframe['Datum'] = pd.to_datetime(dataframe['Datum'])

# parameters for the precalculation
periods = 8760
latitude = 23.614328
longitude = 58.545284
timezone = 'Asia/Muscat'
collector_tilt = 10
collector_azimuth = 180
x = 0.9
a_1 = -0.00159
a_2 = 0.0000977
eta_0 = 0.816
c_1 = 0.0622
c_2 = 0.00023
temp_collector_inlet = 435
temp_collector_outlet = 500

data_precalc = csp_precalc(dataframe, periods,
                           latitude, longitude, timezone,
                           collector_tilt, collector_azimuth, x, a_1, a_2,
                           eta_0, c_1, c_2,
                           temp_collector_inlet, temp_collector_outlet,
                           date_col='Datum')

data_precalc['ES_load_actual_entsoe_power_statistics'] = list(
    dataframe['ES_load_actual_entsoe_power_statistics'].iloc[:periods])
data_precalc.to_csv('CSP_results/precalcs.csv')

# regular oemof_system #

# parameters for energy system
eta_losses = 0.8
elec_consumption = 0.05
backup_costs = 1000
cap_loss = 0.02
conversion_storage = 0.95
costs_storage = economics.annuity(20, 20, 0.06)
costs_electricity = 1000
conversion_factor_turbine = 0.4
size_collector = 1000

# busses
bth = solph.Bus(label='thermal', balanced=True)
bel = solph.Bus(label='electricity')
bcol = solph.Bus(label='solar')

#sources and sinks
col_heat = solph.Source(
    label='collector_heat',
    outputs={bcol: solph.Flow(
        fixed=True,
        actual_value=data_precalc['collector_heat'],
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
        fixed=True,
        actual_value=data_precalc['ES_load_actual_entsoe_power_statistics'],
        nominal_value=1)})

ambience_sol = solph.Sink(
    label='ambience_sol',
    inputs={bcol: solph.Flow()})

collector = solph.Transformer(
    label='collector',
    inputs={
        bcol: solph.Flow(),
        bel: solph.Flow()},
    outputs={bth: solph.Flow()},
    conversion_factors={
        bcol: 1 - elec_consumption,
        bel: elec_consumption,
        bth: eta_losses})

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

date_time_index = pd.date_range('1/1/2003', periods=periods,
                                freq='H', tz=timezone)

energysystem = solph.EnergySystem(timeindex=date_time_index)

energysystem.add(bth, bcol, bel, col_heat, el_grid, backup, consumer,
                 ambience_sol, collector, turbine, storage)

model = solph.Model(energysystem)

model.solve(solver='cbc', solve_kwargs={'tee': True})

# filename = (path + '/lp_files/'
#             + 'CSP_Test.lp')
# model.write(filename, io_options={'symbolic_solver_labels': True})

energysystem.results['main'] = outputlib.processing.results(model)
energysystem.results['meta'] = outputlib.processing.meta_results(model)

collector = outputlib.views.node(energysystem.results['main'], 'electricity')
thermal_bus = outputlib.views.node(energysystem.results['main'], 'thermal')
df = pd.DataFrame()
df = df.append(collector['sequences'])
df = df.join(thermal_bus['sequences'], lsuffix='_1')
df.to_csv('CSP_results/CSP_results.csv')
