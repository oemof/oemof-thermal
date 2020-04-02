# -*- coding: utf-8 -*-

"""Solar thermal collectors

authors:

SPDX-License-Identifier: GPL-3.0-or-later
"""
import os
import sys
import pandas as pd

from oemof import solph
from oemof.tools import economics
import oemof.outputlib as outputlib

from oemof.thermal import facades
from oemof import solph

# import functions to compare lp-files of new example with old one.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tests')))
from test_constraints import compare_lp_files  # noqa


# DATA AND PARAMETERS
######################################################################
# Define parameters for the precalculation
periods = 48
latitude = 52.2443
longitude = 10.5594
timezone = 'Europe/Berlin'
collector_tilt = 10
collector_azimuth = 20
eta_0 = 0.73
a_1 = 1.7
a_2 = 0.016
temp_collector_inlet = 20
delta_temp_n = 10

# Set results path
base_path = os.path.dirname(os.path.abspath(os.path.join(__file__)))

results_path = os.path.join(base_path, 'results')

if not os.path.exists(results_path):
    os.mkdir(results_path)

# Read data for flat collector and heat demand
dataframe = pd.read_csv(
    os.path.join(base_path, 'data', 'data_flat_collector.csv'),
    sep=';',
)

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
######################################################################


######################################################################

# COMPONENT
######################################################################
# busses
bth = solph.Bus(label='thermal')
bel = solph.Bus(label='electricity')

collector = facades.Collector(
    label='solar_collector',
    output_bus=bth,
    electrical_bus=bel,
    dataframe=dataframe,
    periods=periods,
    electrical_consumption=elec_consumption,
    peripheral_losses=eta_losses,
    irradiance_method='horizontal',
    latitude=latitude,
    longitude=longitude,
    collector_tilt=collector_tilt,
    collector_azimuth=collector_azimuth,
    a_1=a_1,
    a_2=a_2,
    eta_0=eta_0,
    temp_collector_inlet=temp_collector_inlet,
    delta_temp_n=delta_temp_n,
    temp_amb=dataframe['temp_amb'],
    date_col='hour',
    irradiance_global_col='global_horizontal_W_m2',
    irradiance_diffuse_col='diffuse_horizontal_W_m2',
    temp_amb_col='temp_amb',
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
collector_excess_heat = solph.Sink(     # todo: Adjust
    label='collector_excess_heat', inputs={bcol: solph.Flow()}
)

# Create collector transformer.
collector = solph.Transformer(     # todo: Adjust
    label='collector',
    inputs={bcol: solph.Flow(), bel: solph.Flow()},
    outputs={bth: solph.Flow()},
    conversion_factors={
        bcol: 1 - elec_consumption,
        bel: elec_consumption,
        bth: 1 - eta_losses,
    },
)

# Create heat storage.
storage = solph.components.GenericStorage(     # todo: Adjust
    label='storage',
    inputs={bth: solph.Flow()},
    outputs={bth: solph.Flow()},
    loss_rate=storage_loss_rate,
    inflow_conversion_factor=conversion_storage,
    outflow_conversion_factor=conversion_storage,
    investment=solph.Investment(ep_costs=costs_storage),
)

date_time_index = pd.date_range(
    '1/1/2003', periods=periods, freq='H', tz='Asia/Muscat'     # todo: Check why tz not 'Europe/Berlin'
)

energysystem = solph.EnergySystem(timeindex=date_time_index)

energysystem.add(
    bth,
    bel,
    el_grid,
    backup,
    collector_excess_heat,
    consumer,
    storage,
    collector,
    collector
)

model = solph.Model(energysystem)

model.solve(solver='cbc', solve_kwargs={'tee': True})

# filename = (path + '/lp_files/'
#             + 'CSP_Test.lp')
# model.write(filename, io_options={'symbolic_solver_labels': True})

model.write('solar_thermal_collector_model_facades.lp', io_options={'symbolic_solver_labels': True})

with open('solar_thermal_collector_model_facades.lp') as generated_file:
    with open('solar_thermal_collector_model.lp') as expected_file:
        compare_lp_files(generated_file, expected_file)
