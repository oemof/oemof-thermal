"""
Example on how to use the 'calc_cops' function to get the
COPs of an exemplary ground-source heat pump (GSHP).

We use the soil temperature as low temperature heat reservoir.
"""

import os
import oemof.thermal.compression_heatpumps_and_chillers as cmpr_hp_chiller
import oemof.solph as solph
import pandas as pd
import matplotlib.pyplot as plt


# Set paths
data_path = os.path.join(os.path.dirname(__file__), 'data/GSHP_example.csv')

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

b_th_high = solph.Bus(label="heat")

b_th_low = solph.Bus(label="heat_low_temp")

energysystem.add(b_el, b_th_high, b_th_low)

energysystem.add(solph.Source(
    label='el_grid',
    outputs={b_el: solph.Flow(variable_costs=10)}))

energysystem.add(solph.Source(
    label='backup_heating',
    outputs={b_th_high: solph.Flow(variable_costs=10)}))

# Borehole that acts as heat source for the heat pump with
# limited extraction heat flow rate
energysystem.add(solph.Source(
    label='ambient',
    outputs={b_th_low: solph.Flow(nominal_value=30)}))

energysystem.add(solph.Sink(
    label='demand',
    inputs={b_th_high: solph.Flow(fix=data['demand_heat'],
                                  nominal_value=1)}))

# Precalculation of COPs
cops_GSHP = cmpr_hp_chiller.calc_cops(
    temp_high=[40],
    temp_low=data['ground_temperature'],
    quality_grade=0.4,
    mode='heat_pump')

# Ground-Source Heat Pump
energysystem.add(solph.Transformer(
    label="GSHP",
    inputs={b_el: solph.Flow(), b_th_low: solph.Flow()},
    outputs={b_th_high: solph.Flow(nominal_value=25, variable_costs=5)},
    conversion_factors={b_el: [1 / cop for cop in cops_GSHP],
                        b_th_low: [(cop - 1) / cop for cop in cops_GSHP]}))

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
GSHP_output = string_results[
    'GSHP', 'heat']['sequences'].values
demand_h = string_results[
    'heat', 'demand']['sequences'].values
GSHP_input = string_results[
    'electricity', 'GSHP']['sequences'].values
env_heat = string_results[
    'ambient', 'heat_low_temp']['sequences'].values

# Example plot
fig2, axs = plt.subplots(3, 1, figsize=(8, 5), sharex=True)
axs[0].plot(GSHP_output, label='heat output')
axs[0].plot(demand_h, linestyle='--', label='heat demand')
axs[0].plot(env_heat, label='heat from environment')
axs[1].plot(cops_GSHP, linestyle='-.')
axs[2].plot(data['ground_temperature'])
axs[0].set_title('Heat Output and Demand')
axs[1].set_title('Coefficient of Performance')
axs[2].set_title('Ground Temperature')
axs[0].legend()

axs[0].grid()
axs[1].grid()
axs[2].grid()
axs[0].set_ylabel('Heat flow in kW')
axs[1].set_ylabel('COP')
axs[2].set_ylabel('Temperature in degC')
axs[2].set_xlabel('Time in h')
plt.tight_layout()
plt.show()

print('********* Main results *********')
print(electricity_bus['sequences'].sum(axis=0))
print(heat_bus['sequences'].sum(axis=0))
print("heat from environment:", env_heat.sum())
