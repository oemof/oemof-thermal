
# import absorption_heatpumps_and_chillers as abs_hp_chiller
import oemof.thermal.absorption_heatpumps_and_chillers as abs_hp_chiller
import oemof.solph as solph
import pandas as pd
import os
import matplotlib.pyplot as plt

solver = 'cbc'
debug = False
number_of_time_steps = 48
solver_verbose = False

date_time_index = pd.date_range('1/1/2012', periods=number_of_time_steps,
                                freq='H')
energysystem = solph.EnergySystem(timeindex=date_time_index)

# Read data file
filename_data = os.path.join(os.path.dirname(__file__), 'data/AC_example.csv')
data = pd.read_csv(filename_data)

filename_charpara = os.path.join(os.path.dirname(__file__),
                                 'data/characteristic_parameters.csv')
charpara = pd.read_csv(filename_charpara)
chiller_name = 'Kuehn'

# Buses with three different temperature levels
b_th_high = solph.Bus(label="hot")
# b_th_medium = solph.Bus(label="cool")
b_th_low = solph.Bus(label="chilled")
energysystem.add(b_th_high, b_th_low)

energysystem.add(solph.Source(
    label='driving_heat',
    outputs={b_th_high: solph.Flow(variable_costs=0)}))
energysystem.add(solph.Source(
    label='cooling_shortage',
    outputs={b_th_low: solph.Flow(variable_costs=20)}))
# energysystem.add(solph.Sink(
#     label='dry_cooling_tower',
#     inputs={b_th_medium: solph.Flow(variable_costs=0)}))
energysystem.add(solph.Sink(
    label='cooling_demand',
    inputs={b_th_low: solph.Flow(fix=True,
                                 nominal_value=35)}))

# Mean cooling water temperature in degC (dry cooling tower)
temp_difference = 4
t_cooling = [t + temp_difference for t in data['air_temperature']]
n = len(t_cooling)

# Pre-Calculations
ddt = abs_hp_chiller.calc_characteristic_temp(
    t_hot=[85],
    t_cool=t_cooling,
    t_chill=[15] * n,
    coef_a=charpara[(charpara['name'] == chiller_name)]['a'].values[0],
    coef_e=charpara[(charpara['name'] == chiller_name)]['e'].values[0],
    method='kuehn_and_ziegler')
Q_dots_evap = abs_hp_chiller.calc_heat_flux(
    ddts=ddt,
    coef_s=charpara[(charpara['name'] == chiller_name)]['s_E'].values[0],
    coef_r=charpara[(charpara['name'] == chiller_name)]['r_E'].values[0],
    method='kuehn_and_ziegler')
Q_dots_gen = abs_hp_chiller.calc_heat_flux(
    ddts=ddt,
    coef_s=charpara[(charpara['name'] == chiller_name)]['s_G'].values[0],
    coef_r=charpara[(charpara['name'] == chiller_name)]['r_G'].values[0],
    method='kuehn_and_ziegler')
COPs = [Qevap / Qgen for Qgen, Qevap in zip(Q_dots_gen, Q_dots_evap)]
nominal_Q_dots_evap = 10
actual_value = [Q_e / nominal_Q_dots_evap for Q_e in Q_dots_evap]
actual_value_df = pd.DataFrame(actual_value).clip(0)

# Absorption Chiller
energysystem.add(solph.Transformer(
    label="AC",
    inputs={b_th_high: solph.Flow()},
    outputs={b_th_low: solph.Flow(nominal_value=nominal_Q_dots_evap,
                                  max=actual_value_df.values,
                                  variable_costs=5)},
    conversion_factors={b_th_low: COPs}))

model = solph.Model(energysystem)

model.solve(solver=solver, solve_kwargs={'tee': solver_verbose})

energysystem.results['main'] = solph.processing.results(model)
energysystem.results['meta'] = solph.processing.meta_results(model)

energysystem.dump(dpath=None, filename=None)


# ****************************************************************************
# ********** PART 2 - Processing the results *********************************
# ****************************************************************************

energysystem = solph.EnergySystem()
energysystem.restore(dpath=None, filename=None)

results = energysystem.results['main']

high_temp_bus = solph.views.node(results, 'hot')
low_temp_bus = solph.views.node(results, 'chilled')

string_results = solph.views.convert_keys_to_strings(
    energysystem.results['main'])
AC_output = string_results[
    'AC', 'chilled']['sequences'].values
demand_cooling = string_results[
    'chilled', 'cooling_demand']['sequences'].values
ASHP_input = string_results[
    'hot', 'AC']['sequences'].values


fig2, axs = plt.subplots(3, 1, figsize=(8, 5), sharex=True)
axs[0].plot(AC_output, label='cooling output')
axs[0].plot(demand_cooling, linestyle='--', label='cooling demand')
axs[1].plot(COPs, linestyle='-.')
axs[2].plot(data['air_temperature'])
axs[0].set_title('Cooling capacity and demand')
axs[1].set_title('Coefficient of Performance')
axs[2].set_title('Air Temperature')
axs[0].legend()

axs[0].grid()
axs[1].grid()
axs[2].grid()
axs[0].set_ylabel('Cooling capacity in kW')
axs[1].set_ylabel('COP')
axs[2].set_ylabel('Temperature in $°$C')
axs[2].set_xlabel('Time in h')
plt.tight_layout()
plt.show()

print('********* Main results *********')
print(high_temp_bus['sequences'].sum(axis=0))
print(low_temp_bus['sequences'].sum(axis=0))
