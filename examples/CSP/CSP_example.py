# -*- coding: utf-8 -*-

"""Solar thermal collectors

authors:

SPDX-License-Identifier: GPL-3.0-or-later
"""

from oemof import solph
from oemof.thermal.CSP import csp_precalc
import pandas as pd
import os
import oemof.outputlib as outputlib

# part of the precaluculations
path = os.path.dirname(os.path.abspath(os.path.join(__file__, '..', '..')))
dataframe = pd.read_csv(path + '/CSP_data/data_CSP.csv', sep=';')
dataframe['Datum'] = pd.to_datetime(dataframe['Datum'])
periods = 8760
data_precalc = csp_precalc(dataframe, periods,
                           23.614328, 58.545284, 'Asia/Muscat',
                           10, 180, 0.9, -0.00159, 0.0000977,
                           0.816, 0.0622, 0.00023,
                           435, 500,
                           date_col='Datum')

data_precalc['Cooling_load_kW'] = list(dataframe['Cooling_load_kW'].iloc[:periods])
data_precalc.to_csv(path + '/CSP_results/precalcs.csv', sep=';')

# regular oemof_system

eta_losses = 0.8
elec_consumption = 0.05
backup_costs = 1000

bth = solph.Bus(label='thermal', balanced=True)
bel = solph.Bus(label='electricity')
bcol = solph.Bus(label='solar')

col_heat = solph.Source(
    label='collector_heat',
    outputs={bcol: solph.Flow(
        fixed=True,
        actual_value=data_precalc['col_heat'],
        nominal_value=1)})

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
            actual_value=data_precalc['Cooling_load_kW'],
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
        bth: eta_losses})

date_time_index = pd.date_range('1/1/2003', periods=periods,
                                freq='H', tz='Asia/Muscat')

energysystem = solph.EnergySystem(timeindex=date_time_index)

energysystem.add(bth, bcol, bel, col_heat, el_grid, backup, consumer, ambience_sol,
                 collector)

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
df.to_csv(path + '/CSP_results/thermal_bus.csv', sep=';')

