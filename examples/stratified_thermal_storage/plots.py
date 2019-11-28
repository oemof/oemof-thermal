import os
import pandas as pd
import matplotlib.pyplot as plt

from oemof.thermal.stratified_thermal_storage import (calculate_storage_u_value,
                                                      calculate_storage_dimensions,
                                                      calculate_capacities,
                                                      calculate_losses)
from oemof.solph import (Bus, Flow,
                         Model, EnergySystem)
from oemof.solph.components import GenericStorage
import oemof.outputlib as outputlib


data_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'stratified_thermal_storage.csv')

input_data = pd.read_csv(data_path, index_col=0, header=0)['var_value']

u_value = calculate_storage_u_value(
    input_data['s_iso'],
    input_data['lamb_iso'],
    input_data['alpha_inside'],
    input_data['alpha_outside'])

volume, surface = calculate_storage_dimensions(
    input_data['height'],
    input_data['diameter']
)

nominal_storage_capacity, max_storage_level, min_storage_level = calculate_capacities(
    volume,
    input_data['temp_h'],
    input_data['temp_c'],
    input_data['nonusable_storage_volume'],
    input_data['heat_capacity'],
    input_data['density'])

loss_rate, fixed_losses_relative, fixed_losses_absolute = calculate_losses(
    u_value,
    input_data['diameter'],
    input_data['temp_h'],
    input_data['temp_c'],
    input_data['temp_env'])

maximum_heat_flow_charging = 2
maximum_heat_flow_discharging = 2


def print_results():
    parameter = {
        'U-value [W/(m2*K)]': u_value,
        'Volume [m3]': volume,
        'Surface [m2]': surface,
        'Nominal storage capacity [MWh]': nominal_storage_capacity,
        'Max. heat flow charging [MW]': maximum_heat_flow_charging,
        'Max. heat flow discharging [MW]': maximum_heat_flow_discharging,
        'Max storage level [-]': max_storage_level,
        'Min storage_level [-]': min_storage_level,
        'Loss rate [-]': loss_rate,
        'Fixed relative losses [-]': fixed_losses_relative,
        'Fixed absolute losses [MWh]': fixed_losses_absolute,
    }

    dash = '-' * 50

    print(dash)
    print('{:>32s}{:>15s}'.format('Parameter name', 'Value'))
    print(dash)

    for name, param in parameter.items():
        print('{:>32s}{:>15.3f}'.format(name, param))

    print(dash)


print_results()

# Set up an energy system model
solver = 'cbc'
periods = 1000
datetimeindex = pd.date_range('1/1/2019', periods=periods, freq='H')

energysystem = EnergySystem(timeindex=datetimeindex)

bus_heat = Bus(label='bus_heat')

thermal_storage_1 = GenericStorage(
    label='thermal_storage_1',
    inputs={bus_heat: Flow(
        nominal_value=maximum_heat_flow_charging,
        variable_costs=0.0001)},
    outputs={bus_heat: Flow(
        nominal_value=maximum_heat_flow_discharging)},
    nominal_storage_capacity=nominal_storage_capacity,
    min_storage_level=min_storage_level,
    max_storage_level=max_storage_level,
    initial_storage_level=0.9,
    loss_rate=loss_rate,
    inflow_conversion_factor=1.,
    outflow_conversion_factor=1.,
    balanced=False
)

thermal_storage_2 = GenericStorage(
    label='thermal_storage_2',
    inputs={bus_heat: Flow(
        nominal_value=maximum_heat_flow_charging,
        variable_costs=0.0001)},
    outputs={bus_heat: Flow(
        nominal_value=maximum_heat_flow_discharging)},
    nominal_storage_capacity=nominal_storage_capacity,
    min_storage_level=min_storage_level,
    max_storage_level=max_storage_level,
    initial_storage_level=0.9,
    loss_rate=loss_rate,
    fixed_losses_relative=fixed_losses_relative,
    fixed_losses_absolute=fixed_losses_absolute,
    inflow_conversion_factor=1.,
    outflow_conversion_factor=1.,
    balanced=False
)

energysystem.add(bus_heat, thermal_storage_1, thermal_storage_2)

# create and solve the optimization model
optimization_model = Model(energysystem)
optimization_model.solve(solver=solver)

# get results
results = outputlib.processing.results(optimization_model)
string_results = outputlib.processing.convert_keys_to_strings(results)
sequences = {k: v['sequences'] for k, v in string_results.items()}
df = pd.concat(sequences, axis=1)

storage_content = df.loc[:, [('thermal_storage_1', 'None', 'capacity'),
                             ('thermal_storage_2', 'None', 'capacity')]]

losses = - storage_content.iloc[1:, :].values + storage_content.iloc[:-1, :].values

# plot storage_content vs. time
fig, ax = plt.subplots(figsize=(8, 5))
df[('thermal_storage_1', 'None', 'capacity')].plot(ax=ax)
df[('thermal_storage_2', 'None', 'capacity')].plot(ax=ax)
ax.set_title('Storage content')
ax.set_xlabel('Timesteps')
ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
plt.tight_layout()
plt.show()

#   losses vs storage content
fig, ax = plt.subplots()
plt.scatter(storage_content[1:], losses)
ax.set_title('Losses vs. storage content')
ax.set_xlabel('Storage content [MWh]')
ax.set_ylabel('Losses [MWh]')
plt.show()

# TODO: losses vs capacity
# TODO: cost function (overnight cost per capacity)
