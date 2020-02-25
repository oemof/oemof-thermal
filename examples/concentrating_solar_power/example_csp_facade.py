import os
import sys
import pandas as pd
import numpy as np

from oemof.thermal import facades
from oemof.thermal.concentrating_solar_power import csp_precalc
from oemof import solph
from oemof.tools import economics

data_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'CSP_data/data_CSP.csv')

input_data = pd.read_csv('CSP_data/data_CSP.csv', sep=';')
input_data['Datum'] = pd.to_datetime(input_data['Datum'])

# Set up an energy system model

periods = 100
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
date_time_index = pd.date_range('1/1/2003', periods=periods,
                                freq='H', tz=timezone)

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
bth = solph.Bus(label='thermal')
bel = solph.Bus(label='electricity')

#sources and sinks
collector = facades.Collector(
    label='solar_collector',
    output=bth,
    electrical_input=bel,
    electrical_consumption=elec_consumption,
    peripheral_losses=eta_losses,
    size=size_collector,
    loss_method='Janotte',
    irradiance_method='horizontal',
    latitude=23.614328,
    longitude=58.545284,
    timezone='Asia/Muscat',
    collector_tilt=10,
    collector_azimuth=180,
    x=0.9,
    a_1=-0.00159,
    a_2=0.0000977,
    eta_0=0.816,
    c_1=0.0622,
    c_2=0.00023,
    temp_collector_inlet=435,
    temp_collector_outlet=500,
    irradiance=input_data['E_dir_hor'],
    temp_amb=input_data['t_amb'],
)

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
        actual_value=input_data['ES_load_actual_entsoe_power_statistics'],
        nominal_value=1)})

excess = solph.Sink(
    label='excess',
    inputs={bth: solph.Flow()})

# transformer and storages

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

energysystem = solph.EnergySystem(timeindex=date_time_index)

energysystem.add(bth, bel, el_grid, backup, excess, consumer, storage, turbine,
                 collector)

# create and solve the optimization model
model = solph.Model(energysystem)
model.solve(solver='cbc', solve_kwargs={'tee': True})
model.write('storage_model_facades.lp', io_options={'symbolic_solver_labels': True})
