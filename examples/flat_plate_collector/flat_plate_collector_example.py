# -*- coding: utf-8 -*-

"""Solar thermal collectors

authors:

SPDX-License-Identifier: GPL-3.0-or-later
"""

from oemof import solph
from oemof.thermal.flat_plate_collector import flat_plate_precalc
import pandas as pd
import os
import oemof.outputlib as outputlib

periods = 48
elec_consumption = 0.02
backup_costs = 40
eta_losses = 0.05

path = os.path.dirname(os.path.abspath(os.path.join(__file__, '..', '..')))
dataframe = pd.read_csv(path + '/CSP_data/data_flat_collector.csv', sep=';')
demand_df = pd.read_csv(path + '/CSP_data/heat_demand.csv', sep=';')
demand = list(demand_df['heat_demand'].iloc[:periods])

precalc_data = flat_plate_precalc(
    dataframe, periods,
    52.2443, 10.5594, 'Europe/Berlin',
    10, 20,
    0.73, 1.7, 0.016,
    20, 10,
    date_col='hour', irradiance_global_col='global_horizontal_W_m2',
    irradiance_diffuse_col='diffuse_horizontal_W_m2',  t_amb_col='t_amb')

precalc_data.to_csv(path + '/CSP_results/flate_plate_precalcs.csv', sep=';')


bth = solph.Bus(label='thermal', balanced=True)
bel = solph.Bus(label='electricity')
bcol = solph.Bus(label='solar')

col_heat = solph.Source(
    label='collector_heat',
    outputs={bcol: solph.Flow(
        fixed=True,
        actual_value=precalc_data['collectors_heat'],
        nominal_value=24)})

el_grid = solph.Source(
    label='grid',
    outputs={bel: solph.Flow()})

backup = solph.Source(
    label='backup',
    outputs={bth: solph.Flow(variable_costs=backup_costs)})

consumer = solph.Sink(
        label='demand',
        inputs={bth: solph.Flow(
            fixed=True,
            actual_value=demand,
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
        bcol: 1-elec_consumption,
        bel: elec_consumption,
        bth: 1-eta_losses})

storage = solph.components.GenericStorage(
    label='storage',
    inputs={bth: solph.Flow()},
    outputs={bth: solph.Flow()},
    loss_rate=0.001, nominal_storage_capacity=4000,
    inflow_conversion_factor=0.98, outflow_conversion_factor=0.8)

date_time_index = pd.date_range('1/1/2003', periods=periods,
                                freq='H', tz='Asia/Muscat')

energysystem = solph.EnergySystem(timeindex=date_time_index)

energysystem.add(bth, bcol, bel, col_heat, el_grid, backup, consumer,
                 ambience_sol, storage, collector)

model = solph.Model(energysystem)

model.solve(solver='cbc', solve_kwargs={'tee': True})

# filename = (path + '/lp_files/'
#             + 'CSP_Test.lp')
# model.write(filename, io_options={'symbolic_solver_labels': True})

energysystem.results['main'] = outputlib.processing.results(model)
energysystem.results['meta'] = outputlib.processing.meta_results(model)

collector = outputlib.views.node(energysystem.results['main'], 'collector')
thermal_bus = outputlib.views.node(energysystem.results['main'], 'thermal')
df = pd.DataFrame()
df = df.append(collector['sequences'])
df = df.join(thermal_bus['sequences'], lsuffix='_1')
df.to_csv(path + '/CSP_results/thermal_bus_flat_plate.csv', sep=';')
