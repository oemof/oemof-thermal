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


input_data = pd.read_csv('stratified_thermal_storage.csv', index_col=0, header=0)['var_value']

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

loss_rate, fixed_losses = calculate_losses(
    nominal_storage_capacity,
    u_value,
    surface,
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
        'Fixed losses [-]': fixed_losses
    }

    dash = '-' * 42

    print(dash)
    print('{:>32s}{:>15s}'.format('Parameter name', 'Value'))
    print(dash)

    for name, param in parameter.items():
        print('{:>32s}{:>15.3f}'.format(name, param))

    print(dash)


print_results()

# Set up an energy system model
solver = 'cbc'
periods = 500
datetimeindex = pd.date_range('1/1/2019', periods=periods, freq='H')

energysystem = EnergySystem(timeindex=datetimeindex)

bus_heat = Bus(label='bus_heat')

thermal_storage = GenericStorage(
    label='thermal_storage',
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
    fixed_losses=fixed_losses,
    inflow_conversion_factor=1.,
    outflow_conversion_factor=1.,
    balanced=False
)

energysystem.add(bus_heat, thermal_storage)

# create and solve the optimization model
optimization_model = Model(energysystem)
optimization_model.solve(solver=solver)

# get results
results = outputlib.processing.results(optimization_model)
string_results = outputlib.processing.convert_keys_to_strings(results)
sequences = {k:v['sequences'] for k, v in string_results.items()}
df = pd.concat(sequences, axis=1)

# plot storage_content vs. time
fig, ax = plt.subplots()
df[('thermal_storage', 'None', 'capacity')].plot.area(ax=ax)
ax.set_title('Storage content')
ax.set_xlabel('Timesteps')
ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
plt.tight_layout()
plt.show()

storage_content = df[('thermal_storage', 'None', 'capacity')][10:-5].values
losses = - storage_content[1:] + storage_content[:-1]

#   losses vs storage content
fig, ax = plt.subplots()
plt.scatter(storage_content[:-1], losses)
ax.set_title('Losses vs. storage content')
ax.set_xlabel('Storage content [MWh]')
ax.set_ylabel('Losses [MWh]')
plt.show()

# TODO: losses vs capacity
# TODO: cost function (overnight cost per capacity)
