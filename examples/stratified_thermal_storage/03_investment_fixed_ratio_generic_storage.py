"""
This example shows how to invest into nominal_storage_capacity and capacity
(charging/discharging power) with a fixed ratio. Pass invest_relation_input_capacity and
invest_relation_input_output and set equivalent periodical costs on at least one of the
Investment objects.
"""

import os
import pandas as pd
import numpy as np

from oemof.thermal.stratified_thermal_storage import (calculate_storage_u_value,
                                                      calculate_losses)
from oemof.solph import (Source, Sink, Bus, Flow,
                         Investment, Model, EnergySystem)
from oemof.solph.components import GenericStorage
from oemof.solph import processing


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

loss_rate, fixed_losses_relative, fixed_losses_absolute = calculate_losses(
    u_value,
    input_data['diameter'],
    input_data['temp_h'],
    input_data['temp_c'],
    input_data['temp_env'])


def print_parameters():
    parameter = {
        'EQ-cost [Eur/]': 0,
        'U-value [W/(m2*K)]': u_value,
        'Loss rate [-]': loss_rate,
        'Fixed relative losses [-]': fixed_losses_relative,
        'Fixed absolute losses [MWh]': fixed_losses_absolute,
    }

    dash = '-' * 50

    print(dash)
    print('{:>32s}{:>15s}'.format('Parameter name', 'Value'))
    print(dash)

    for name, param in parameter.items():
        print('{:>32s}{:>15.5f}'.format(name, param))

    print(dash)


print_parameters()

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

thermal_storage = GenericStorage(
    label='thermal_storage',
    inputs={bus_heat: Flow(
        investment=Investment())},
    outputs={bus_heat: Flow(
        investment=Investment(),
        variable_costs=0.0001)},
    min_storage_level=input_data['min_storage_level'],
    max_storage_level=input_data['max_storage_level'],
    loss_rate=loss_rate,
    fixed_losses_relative=fixed_losses_relative,
    fixed_losses_absolute=fixed_losses_absolute,
    inflow_conversion_factor=input_data['inflow_conversion_factor'],
    outflow_conversion_factor=input_data['outflow_conversion_factor'],
    invest_relation_input_output=1,
    invest_relation_input_capacity=1 / 6,
    investment=Investment(ep_costs=400, minimum=1)
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
maximum_heat_flow_charging = results[bus_heat, thermal_storage]['scalars']['invest']

dash = '-' * 50
print(dash)
print('{:>32s}{:>15.3f}'.format('Invested capacity [MW]', maximum_heat_flow_charging))
print('{:>32s}{:>15.3f}'.format('Invested storage capacity [MWh]', built_storage_capacity))
print(dash)
