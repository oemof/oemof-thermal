import os
import pandas as pd
import oemof.outputlib as outputlib
import matplotlib.pyplot as plt


from oemof.thermal import facades
from oemof import solph
from oemof.tools import economics


# set paths
base_path = os.path.dirname(os.path.abspath(os.path.join(__file__)))

results_path = os.path.join(base_path, 'results/')
lp_path = os.path.join(base_path, 'lp_files/')
data_path = os.path.join(base_path, 'csp_data/')

if not os.path.exists(results_path):
    os.mkdir(results_path)


# Set up an energy system model
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

input_data = pd.read_csv(data_path + 'data_csp_plant.csv').head(periods)
input_data['Datum'] = pd.to_datetime(input_data['Datum'])
input_data.set_index('Datum', inplace=True)
input_data.index = input_data.index.tz_localize(tz='Asia/Muscat')

date_time_index = input_data.index


# regular oemof_system #

# parameters for energy system
additional_losses = 0.2
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

# collector
collector = facades.Collector(
    label='solar_collector',
    heat_bus=bth,
    electrical_bus=bel,
    electrical_consumption=elec_consumption,
    additional_losses=additional_losses,
    aperture_area=size_collector,
    loss_method='Janotte',
    irradiance_method='horizontal',
    latitude=latitude,
    longitude=longitude,
    collector_tilt=collector_tilt,
    collector_azimuth=collector_azimuth,
    cleanliness=cleanliness,
    a_1=a_1,
    a_2=a_2,
    eta_0=eta_0,
    c_1=c_1,
    c_2=c_2,
    temp_collector_inlet=temp_collector_inlet,
    temp_collector_outlet=temp_collector_outlet,
    temp_amb=input_data['t_amb'],
    irradiance=input_data['E_dir_hor'])

# sources and sinks
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

 # build the system and solve the problem  
energysystem = solph.EnergySystem(timeindex=date_time_index)

energysystem.add(bth, bel, el_grid, backup, excess, consumer, storage, turbine,
                 collector)

# create and solve the optimization model
model = solph.Model(energysystem)
model.solve(solver='cbc', solve_kwargs={'tee': True})

# if not os.path.exists(lp_path):
#         os.mkdir(lp_path)
# model.write(lp_path + 'csp_model_facades.lp',
#             io_options={'symbolic_solver_labels': True})


results = outputlib.processing.results(model)

collector_inflow = outputlib.views.node(
    results, 'solar_collector-inflow')['sequences']
thermal_bus = outputlib.views.node(results, 'thermal')['sequences']
electricity_bus = outputlib.views.node(results, 'electricity')['sequences']
df = pd.DataFrame()
df = df.append(collector_inflow)
df = df.join(thermal_bus, lsuffix='_1')
df = df.join(electricity_bus, lsuffix='_1')
df.to_csv(results_path + 'facade_results.csv')

fig, ax = plt.subplots()
ax.plot(list(range(periods)), thermal_bus[(('solar_collector', 'thermal'), 'flow')])
ax.set(xlabel='time [h]', ylabel='Q_coll [W/m2]',
       title='Heat of the collector')
ax.grid()
ax.legend()
plt.show()
