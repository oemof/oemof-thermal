# -*- coding: utf-8 -*-

"""Solar thermal collectors

authors:

SPDX-License-Identifier: GPL-3.0-or-later
"""

from oemof import solph
from oemof.thermal.flat_plate_collector import flat_plate_precalc
from oemof.tools import economics
from demandlib import bdew as bdew
from workalendar.europe import Germany
from flat_plate_collector_plot_example import plot_collector_heat
import pandas as pd
import os
import oemof.outputlib as outputlib

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
c_1 = 1.7
c_2 = 0.016
temp_collector_inlet = 20
delta_temp_n = 10

# Read data for flat collector and heat demand
path = os.path.dirname(os.path.abspath(os.path.join(__file__, '..', '..')))
dataframe = pd.read_csv(
    path + '/examples/flat_plate_collector/data/data_flat_collector.csv',
    sep=';',
)

# # Read demand time series from csv file
# # --------------------------------------------------------------
# demand_df = pd.read_csv(
#     path + '/examples/flat_plate_collector/data/heat_demand.csv', sep=';'
# )
# demand = list(demand_df['heat_demand'].iloc[:periods])
# # --------------------------------------------------------------

# Use demandlib for creation of demand time series
# --------------------------------------------------------------
temperature = pd.read_csv(
    path + '/examples/flat_plate_collector/data/temperature_data.csv', sep=','
)['temperature']

cal = Germany()
holidays = dict(cal.holidays(2018))

# Create a DataFrame to hold the timeseries
demand_df = pd.DataFrame(
    index=pd.date_range(pd.datetime(2010, 1, 1, 0), periods=8760, freq='H')
)


# Single family house (efh: Einfamilienhaus)
demand_df['efh'] = bdew.HeatBuilding(
    demand_df.index,
    holidays=holidays,
    temperature=temperature,
    shlp_type='EFH',
    building_class=1,
    wind_class=1,
    annual_heat_demand=25000,
    name='EFH',
).get_bdew_profile()

# Multi family house (mfh: Mehrfamilienhaus)
demand_df['mfh'] = bdew.HeatBuilding(
    demand_df.index,
    holidays=holidays,
    temperature=temperature,
    shlp_type='MFH',
    building_class=2,
    wind_class=0,
    annual_heat_demand=80000,
    name='MFH',
).get_bdew_profile()

# Industry, trade, service (ghd: Gewerbe, Handel, Dienstleistung)
demand_df['ghd'] = bdew.HeatBuilding(
    demand_df.index,
    holidays=holidays,
    temperature=temperature,
    shlp_type='ghd',
    wind_class=0,
    annual_heat_demand=140000,
    name='ghd',
).get_bdew_profile()

demand = demand_df.sum(axis=1)
# --------------------------------------------------------------

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

# PRECALCULATION
######################################################################
# Calculate global irradiance on the collector area
# and collector efficiency depending on the temperature difference
precalc_data = flat_plate_precalc(
    dataframe,
    periods,
    latitude,
    longitude,
    timezone,
    collector_tilt,
    collector_azimuth,
    eta_0,
    c_1,
    c_2,
    temp_collector_inlet,
    delta_temp_n,
    date_col='hour',
    irradiance_global_col='global_horizontal_W_m2',
    irradiance_diffuse_col='diffuse_horizontal_W_m2',
    t_amb_col='t_amb',
)

precalc_data.to_csv(
    path + '/examples/flat_plate_collector/results/flate_plate_precalcs.csv',
    sep=';',
)
######################################################################

# COMPONENT
######################################################################
# Create busses
bth = solph.Bus(label='thermal', balanced=True)
bel = solph.Bus(label='electricity')
bcol = solph.Bus(label='solar')

# Create source for collector heat. Actual value is the precalculated collector heat.
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
    label='collector_excess_heat', inputs={bcol: solph.Flow()}
)

# Create collector transformer.
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

date_time_index = pd.date_range(
    '1/1/2003', periods=periods, freq='H', tz='Asia/Muscat'
)

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
df.to_csv(
    path + '/examples/flat_plate_collector/results/thermal_bus_flat_plate.csv',
    sep=';',
)


plot_collector_heat(precalc_data, periods, eta_0)
