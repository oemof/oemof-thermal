"""
This example shows how to invest into nominal_storage_capacity and capacity
(charging/discharging power) independently with no fixed ratio. There is still a
fixed ratio between input and output capacity which makes sense for a sensible heat storage.
Make sure to pass both capacity_cost and storage_capacity_cost.
"""

import os
import pandas as pd
import numpy as np

from oemof.thermal.stratified_thermal_storage import calculate_storage_u_value
from oemof.thermal import facades

from oemof.solph import (processing, Source, Sink, Bus, Flow,
                         Model, EnergySystem)


# Set paths
data_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'data/stratified_thermal_storage.csv')

# Read input data
input_data = pd.read_csv(data_path, index_col=0, header=0)['var_value']

# Precalculation
u_value = calculate_storage_u_value(
    input_data['s_iso'],
    input_data['lamb_iso'],
    input_data['alpha_inside'],
    input_data['alpha_outside'])

# Set up an energy system model
solver = 'cbc'
periods = 100
datetimeindex = pd.date_range('1/1/2019', periods=periods, freq='H')
demand_timeseries = np.zeros(periods)
demand_timeseries[-5:] = 1
heat_feedin_timeseries = np.zeros(periods)
heat_feedin_timeseries[:10] = 1

energysystem = EnergySystem(timeindex=datetimeindex)

bus_heat = Bus(label='bus_heat')

heat_source = Source(
    label='heat_source',
    outputs={bus_heat: Flow(
        nominal_value=1,
        fix=heat_feedin_timeseries)})

shortage = Source(
    label='shortage',
    outputs={bus_heat: Flow(variable_costs=1e6)})

excess = Sink(
    label='excess',
    inputs={bus_heat: Flow()})

heat_demand = Sink(
    label='heat_demand',
    inputs={bus_heat: Flow(
        nominal_value=1,
        fix=demand_timeseries)})

thermal_storage = facades.StratifiedThermalStorage(
    label='thermal_storage',
    bus=bus_heat,
    diameter=input_data['diameter'],  # TODO: setting to zero should give an error
    temp_h=input_data['temp_h'],
    temp_c=input_data['temp_c'],
    temp_env=input_data['temp_env'],
    u_value=u_value,
    expandable=True,
    capacity_cost=50,
    storage_capacity_cost=400,
    minimum_storage_capacity=1,  # TODO: setting to zero should give an error!
    min_storage_level=input_data['min_storage_level'],
    max_storage_level=input_data['max_storage_level'],
    efficiency=input_data['efficiency'],
    marginal_cost=0.0001
)

energysystem.add(bus_heat, heat_source, shortage, excess, heat_demand, thermal_storage)

# Create and solve the optimization model
optimization_model = Model(energysystem)
optimization_model.solve(solver=solver,
                         solve_kwargs={'tee': False, 'keepfiles': False})

# Get results
results = processing.results(optimization_model)
string_results = processing.convert_keys_to_strings(results)
sequences = {k: v['sequences'] for k, v in string_results.items()}
df = pd.concat(sequences, axis=1)

# Print storage sizing
built_storage_capacity = results[thermal_storage, None]['scalars']['invest']
initial_storage_capacity = results[thermal_storage, None]['scalars']['init_content']
built_capacity = results[bus_heat, thermal_storage]['scalars']['invest']

dash = '-' * 50
print(dash)
print('{:>32s}{:>15.3f}'.format('Invested capacity [MW]', built_capacity))
print('{:>32s}{:>15.3f}'.format('Invested storage capacity [MWh]', built_storage_capacity))
print(dash)
