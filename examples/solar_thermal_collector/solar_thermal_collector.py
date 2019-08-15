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
periods = 100

data_precalc = csp_precalc(dataframe, periods,
                           23.614328, 58.545284, 'Asia/Muscat',
                           10, 180, 0.9, -0.00159, 0.0000977,
                           0.816, 0.0622, 0.00023,
                           435, 500,
                           date_col='Datum')

data_precalc['Cooling_load_kW'] = list(dataframe['Cooling_load_kW'].iloc[:periods])
data_precalc.to_csv(path + '/CSP_results/precalcs.csv', sep=';')

# regular oemof_system

eta_losses = 0.2
elec_consumption = 0.05

bth = solph.Bus(label='thermal', balanced=True)
bel = solph.Bus(label='electricity')
bsol = solph.Bus(label='solar')
bam = solph.Bus(label="ambient")

sun = solph.Source(
    label='sun',
    outputs={bsol: solph.Flow(
        fixed=True,
        actual_value=data_precalc['col_ira'],
        nominal_value=10)})

el_grid = solph.Source(
    label='grid',
    outputs={bel: solph.Flow()})

backup = solph.Source(
    label='backup',
    outputs={bth: solph.Flow(variable_costs=1000)})

consumer = solph.Sink(
        label='demand',
        inputs={bth: solph.Flow(
            fixed=True,
            actual_value=data_precalc['Cooling_load_kW'],
            nominal_value=1)})

ambience = solph.Sink(
    label='ambience',
    inputs={bam: solph.Flow()})

ambience_sol = solph.Sink(
    label='ambience_sol',
    inputs={bsol: solph.Flow()})

collector = solph.Transformer(
    label='collector',
    inputs={
        bsol: solph.Flow(),
        bel: solph.Flow()},
    outputs={bth: solph.Flow(nominal_value=10),
             bam: solph.Flow()},
    conversion_factors={
        bsol: data_precalc['eta_c'],
        bel: elec_consumption,
        bth: 1-eta_losses})

date_time_index = pd.date_range('1/1/2003', periods=periods,
                                freq='H', tz='Asia/Muscat')

energysystem = solph.EnergySystem(timeindex=date_time_index)

energysystem.add(bth, bsol, bel, bam, sun, el_grid, backup, consumer, ambience,
                 ambience_sol, collector)

model = solph.Model(energysystem)

model.solve(solver='cbc', solve_kwargs={'tee': True})

energysystem.results['main'] = outputlib.processing.results(model)

thermal_bus = outputlib.views.node(energysystem.results['main'], 'thermal')
thermal_bus['sequences'].to_csv(path + '/CSP_results/thermal_bus.csv', sep=';')

