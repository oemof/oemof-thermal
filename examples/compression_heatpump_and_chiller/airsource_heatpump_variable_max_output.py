"""
Example on how to use the 'calc_cops' function to get the
COPs of an exemplary air-source heat pump (ASHP) and use the
pre-calculated COPs in a solph.Transformer.
Furthermore, the maximal possible heat output of the heat pump is
pre-calculated and varies with the temperature levels of the heat reservoirs.

We use the ambient air as low temperature heat reservoir.
"""

import os
import oemof.thermal.compression_heatpumps_and_chillers as cmpr_hp_chiller
import oemof.solph as solph
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Set paths
data_path = os.path.join(os.path.dirname(__file__), 'data/ASHP_example.csv')

# Read input data
data = pd.read_csv(data_path)

# Set up an energy system model
solver = 'cbc'
number_of_time_steps = 24
solver_verbose = False

date_time_index = pd.date_range('1/1/2012', periods=number_of_time_steps,
                                freq='H')

energysystem = solph.EnergySystem(timeindex=date_time_index)

b_el = solph.Bus(label="electricity")

b_heat = solph.Bus(label="heat")

energysystem.add(b_el, b_heat)

energysystem.add(solph.Source(
    label='el_grid',
    outputs={b_el: solph.Flow(variable_costs=10)}))

energysystem.add(solph.Source(
    label='backup_heating',
    outputs={b_heat: solph.Flow(variable_costs=10)}))

energysystem.add(solph.Sink(
    label='demand',
    inputs={b_heat: solph.Flow(fix=data['demand_heat'],
                               nominal_value=1)}))

temp_threshold_icing = 2

# Precalculation of COPs
cops_ASHP = cmpr_hp_chiller.calc_cops(
    temp_high=[40],
    temp_low=data['ambient_temperature'],
    quality_grade=0.4,
    mode='heat_pump',
    temp_threshold_icing=temp_threshold_icing,
    factor_icing=0.8)

# Define operation condition for nominal output
nominal_conditions = {'nominal_Q_hot': 25,
                      'nominal_el_consumption': 7}


max_Q_dot_heating = cmpr_hp_chiller.calc_max_Q_dot_heat(nominal_conditions,
                                                        cops_ASHP)

# Air-Source Heat Pump
energysystem.add(solph.Transformer(
    label="ASHP",
    inputs={b_el: solph.Flow()},
    outputs={b_heat: solph.Flow(
        nominal_value=nominal_conditions['nominal_Q_hot'],
        max=max_Q_dot_heating,
        variable_costs=5)},
    conversion_factors={b_heat: cops_ASHP}))

# Create and solve the optimization model
model = solph.Model(energysystem)
model.solve(solver=solver, solve_kwargs={'tee': solver_verbose})

# Get results
energysystem.results['main'] = solph.processing.results(model)
energysystem.results['meta'] = solph.processing.meta_results(model)

energysystem.dump(dpath=None, filename=None)

# Processing the results
energysystem = solph.EnergySystem()
energysystem.restore(dpath=None, filename=None)

results = energysystem.results['main']

electricity_bus = solph.views.node(results, 'electricity')
heat_bus = solph.views.node(results, 'heat')

string_results = solph.views.convert_keys_to_strings(
    energysystem.results['main'])
ASHP_output = string_results[
    'ASHP', 'heat']['sequences'].values
demand_h = string_results[
    'heat', 'demand']['sequences'].values
ASHP_input = string_results[
    'electricity', 'ASHP']['sequences'].values

# Absolute values of maximal heating capacity
max_Q_dot_heating_abs = [nominal_conditions['nominal_Q_hot'] * max_heating for
                         max_heating in max_Q_dot_heating]

# Example plot
fig, axs = plt.subplots(3, 1, figsize=(8, 5), sharex=True)
axs[0].plot(max_Q_dot_heating_abs,
            linestyle='-.',
            label='max heat output')
axs[0].plot(ASHP_output, label='actual heat output')
axs[0].plot(demand_h, linestyle='--', label='heat demand')
axs[1].plot(cops_ASHP, linestyle='-.')
axs[2].plot([-1, number_of_time_steps],
            [temp_threshold_icing, temp_threshold_icing],
            linestyle='--',
            color='red',
            label='threshold temperature')
axs[2].text(x=number_of_time_steps - 1,
            y=temp_threshold_icing,
            s='threshold temperature',
            ha='right',
            va='center',
            color='red',
            fontsize=10,
            bbox=dict(facecolor='white', edgecolor='white', alpha=0.9))
axs[2].plot(data['ambient_temperature'])
axs[0].set_title('Heat Output and Demand')
axs[1].set_title('Coefficient of Performance')
axs[2].set_title('Source Temperature (Ambient)')
axs[0].legend()

axs[0].grid()
axs[1].grid()
axs[2].grid()
axs[0].set_xlim(0, number_of_time_steps)
axs[0].set_ylabel('Heat flow in kW')
axs[1].set_ylabel('COP')
axs[2].set_ylabel('Temperature in $°$C')
axs[2].set_xlabel('Time in h')
plt.tight_layout()
plt.show()

# print('********* Main results *********')
# print(electricity_bus['sequences'].sum(axis=0))
# print(heat_bus['sequences'].sum(axis=0))
print('********* Main results *********')
print("Total electricity consumption: {:2.1f}".format(
    ASHP_input.sum(axis=0)[0]))
print("Total heat output: {:2.1f}".format(
    ASHP_output.sum(axis=0)[0]))
print("Average Coefficient of Performance (COP): {:2.2f}".format(
    np.mean(cops_ASHP)))
print("Seasonal Performance Factor (SPF): {:2.2f}".format(
    ASHP_output.sum(axis=0)[0] / ASHP_input.sum(axis=0)[0]))
