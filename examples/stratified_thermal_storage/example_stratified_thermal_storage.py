import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from oemof.thermal.stratified_thermal_storage import (calculate_storage_u_value,
                                                      calculate_capacities,
                                                      calculate_losses)
from oemof.solph import (Source, Sink, Transformer, Bus, Flow,
                         Model, EnergySystem)
from oemof.solph.components import GenericStorage
import oemof.outputlib as outputlib

solver = 'cbc'

# set timeindex and create data
periods = 20
datetimeindex = pd.date_range('1/1/2019', periods=periods, freq='H')
x = np.arange(periods)
demand = np.zeros(20)
demand[-3:] = 2
wind = np.zeros(20)
wind[:3] = 3

# set up EnergySystem
energysystem = EnergySystem(timeindex=datetimeindex)

b_el = Bus(label='electricity')

wind = Source(label='wind', outputs={b_el: Flow(nominal_value=1,
                                                actual_value=wind,
                                                fixed=True)})

shortage = Source(label='shortage', outputs={b_el: Flow(variable_costs=1e6)})

excess = Sink(label='excess', inputs={b_el: Flow()})

demand = Sink(label='demand', inputs={b_el: Flow(nominal_value=1,
                                                 actual_value=demand,
                                                 fixed=True)})

height = 10 # [m]
diameter = 4 # [m]
density = 971.78 # [kg/m3]
heat_capacity = 4180 # [J/kgK]
temp_h = 95 # [degC]
temp_c = 60 # [degC]
temp_env = 10 # [degC]
inflow_conversion_factor = 0.9
outflow_conversion_factor = 0.9
nonusable_storage_volume = 0.2
s_iso = 0.05 # [m]
lamb_iso = 0.03 # [W/(m*K)]
alpha_inside = 1 # [W/(m2*K)]
alpha_outside = 1 # [W/(m2*K)]

u_value = calculate_storage_u_value(s_iso, lamb_iso, alpha_inside, alpha_outside)

nominal_storage_capacity, surface, max_storage_level, min_storage_level = calculate_capacities(height, diameter, temp_h, temp_c, nonusable_storage_volume)

loss_rate, loss_constant = calculate_losses(nominal_storage_capacity, u_value, surface, temp_h, temp_c, temp_env)

print(nominal_storage_capacity, min_storage_level, max_storage_level, loss_rate, loss_constant)

# storage = GenericStorage(label='storage',
#                          inputs={b_el: Flow(variable_costs=0.0001)},
#                          outputs={b_el: Flow()},
#                          nominal_storage_capacity=nominal_storage_capacity,
#                          initial_storage_level=0.75,
#                          min_storage_level=min_storage_level,
#                          max_storage_level=max_storage_level,
#                          loss_rate=loss_rate,
#                          loss_constant=loss_constant,
#                          inflow_conversion_factor=1.,
#                          outflow_conversion_factor=1.)

storage = GenericStorage(label='storage',
                         inputs={b_el: Flow(variable_costs=0.0001)},
                         outputs={b_el: Flow()},
                         nominal_storage_capacity=15,
                         initial_storage_level=0.75,
                         #min_storage_level=0.4,
                         #max_storage_level=0.9,
                         loss_rate=0.1,
                         loss_constant=0.,
                         inflow_conversion_factor=1.,
                         outflow_conversion_factor=1.)

energysystem.add(b_el, wind, shortage, excess, demand, storage)

# create and solve the optimization model
optimization_model = Model(energysystem)
optimization_model.write('/home/jann/Desktop/storage_model.lp', io_options={'symbolic_solver_labels': True})
optimization_model.solve(solver=solver,
                         solve_kwargs={'tee': False, 'keepfiles': False})
# get results
results = outputlib.processing.results(optimization_model)
string_results = outputlib.processing.convert_keys_to_strings(results)
sequences = {k:v['sequences'] for k, v in string_results.items()}
df = pd.concat(sequences, axis=1)

# print and plot results
df = df.reset_index()
print(df)

fig, (ax1, ax2) = plt.subplots(2, 1)
df[[('shortage', 'electricity', 'flow'),
    ('wind', 'electricity', 'flow'),
    ('storage', 'electricity', 'flow')]].plot.bar(ax=ax1, stacked=True, color=['y', 'b', 'k'])
(-df[('electricity', 'storage', 'flow')]).plot.bar(ax=ax1, color='g')
df[('electricity', 'demand', 'flow')].plot(ax=ax1, linestyle='', marker='o', color='r')
ax1.set_ylim(-5, 5)
ax1.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
df[('storage', 'None', 'capacity')].plot.bar(ax=ax2)
ax2.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
plt.tight_layout()
plt.show()