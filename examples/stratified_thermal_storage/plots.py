"""
For this script to work as intended, please use oemof-solph v0.4.0 or higher
to ensure that the GenericStorage has the attributes
`fixed_losses_absolute` and `fixed_losses_relative`.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


from oemof.thermal.stratified_thermal_storage import (
    calculate_storage_u_value,
    calculate_storage_dimensions,
    calculate_capacities,
    calculate_losses,
)
from oemof.solph import processing, views, Bus, Flow, Model, EnergySystem
from oemof.solph.components import GenericStorage


# Set paths
data_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'data', 'stratified_thermal_storage.csv')

input_data = pd.read_csv(data_path, index_col=0, header=0)['var_value']

u_value = calculate_storage_u_value(
    input_data['s_iso'],
    input_data['lamb_iso'],
    input_data['alpha_inside'],
    input_data['alpha_outside']
)

volume, surface = calculate_storage_dimensions(
    input_data['height'],
    input_data['diameter']
)

nominal_storage_capacity = calculate_capacities(
    volume,
    input_data['temp_h'],
    input_data['temp_c']
)

loss_rate, fixed_losses_relative, fixed_losses_absolute = calculate_losses(
    u_value,
    input_data['diameter'],
    input_data['temp_h'],
    input_data['temp_c'],
    input_data['temp_env'],
)


def print_results():
    parameter = {
        'U-value [W/(m2*K)]': u_value,
        'Volume [m3]': volume,
        'Surface [m2]': surface,
        'Nominal storage capacity [MWh]': nominal_storage_capacity,
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


print_results()

# Set up an energy system model
solver = 'cbc'
periods = 800
datetimeindex = pd.date_range('1/1/2019', periods=periods, freq='H')

energysystem = EnergySystem(timeindex=datetimeindex)

storage_list = []

bus_simple_thermal_storage = Bus(label='bus_simple_thermal_storage', balanced=False)

energysystem.add(bus_simple_thermal_storage)

storage_list.append(GenericStorage(
    label='simple_thermal_storage',
    inputs={bus_simple_thermal_storage: Flow(
        nominal_value=input_data['maximum_heat_flow_charging'],
        variable_costs=0.0001)},
    outputs={bus_simple_thermal_storage: Flow(
        nominal_value=input_data['maximum_heat_flow_discharging'],
        variable_costs=0.0001)},
    nominal_storage_capacity=nominal_storage_capacity,
    min_storage_level=input_data['min_storage_level'],
    max_storage_level=input_data['max_storage_level'],
    initial_storage_level=27 / nominal_storage_capacity,
    loss_rate=0.001,
    inflow_conversion_factor=1.,
    outflow_conversion_factor=1.,
    balanced=False
))

for i, nominal_storage_capacity in enumerate([30, 65, 90]):
    bus_i = Bus(label=f'bus_{i}', balanced=False)

    energysystem.add(bus_i)

    storage_list.append(GenericStorage(
        label=f'stratified_thermal_storage_{nominal_storage_capacity}_MWh',
        inputs={bus_i: Flow(
            nominal_value=input_data['maximum_heat_flow_charging'],
            variable_costs=0.0001)},
        outputs={bus_i: Flow(
            nominal_value=input_data['maximum_heat_flow_discharging'],
            variable_costs=0.0001)},
        nominal_storage_capacity=nominal_storage_capacity,
        min_storage_level=input_data['min_storage_level'],
        max_storage_level=input_data['max_storage_level'],
        initial_storage_level=27 / nominal_storage_capacity,
        loss_rate=loss_rate,
        fixed_losses_relative=fixed_losses_relative,
        fixed_losses_absolute=fixed_losses_absolute,
        inflow_conversion_factor=1.,
        outflow_conversion_factor=1.,
        balanced=False
    ))

energysystem.add(*storage_list)

# Create and solve the optimization model
optimization_model = Model(energysystem)
optimization_model.solve(solver=solver)

# Get results
results = processing.results(optimization_model)

storage_content = views.node_weight_by_type(results, GenericStorage)\
    .reset_index(drop=True)

storage_content.columns = storage_content.columns\
    .set_levels([k.label for k in storage_content.columns.levels[0]], level=0)

losses = - storage_content.iloc[1:, :].reset_index(drop=True)\
    + storage_content.iloc[:-1, :].reset_index(drop=True)

losses.columns = losses.columns.set_levels(['losses'], level=1)

storage_content = storage_content.iloc[:-1, :]

storage_df = pd.concat([storage_content, losses], 1)

storage_df = storage_df.reindex(sorted(storage_df.columns), axis=1)

# Plot storage_content vs. time
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
storage_content.plot(ax=ax1)
ax1.set_title('Storage content')
ax1.set_xlabel('Timesteps')
ax1.set_ylabel('Storage content [MWh]')
ax1.grid(alpha=0.3)
ax1.get_legend().remove()

# Plot losses vs storage content
for storage_label in (storage.label for storage in storage_list):
    ax2.scatter(
        storage_df[(storage_label, 'storage_content')],
        storage_df[(storage_label, 'losses')],
        label=storage_label,
        s=1
    )
ax2.set_xlim(0, 27.2)
ax2.set_ylim(0, 0.035)
ax2.set_title('Losses vs. storage content')
ax2.set_xlabel('Storage content [MWh]')
ax2.set_ylabel('Losses [MW]')
ax2.grid(alpha=0.3)
ax2.legend(markerscale=8, loc='center left', bbox_to_anchor=(1.0, 0.5))
plt.tight_layout()
plt.savefig('compare_storage_models.svg')
