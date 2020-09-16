import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import oemof.solph as solph
from oemof.thermal.stratified_thermal_storage import (  # noqa
    calculate_storage_u_value,
    calculate_storage_dimensions,
    calculate_capacities
)
from oemof.thermal import facades

Source = solph.Source
Sink = solph.Sink
Bus = solph.Bus
Flow = solph.Flow
Model = solph.Model
EnergySystem = solph.EnergySystem

data_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    './data/validation_data.csv')

input_data = pd.read_csv(data_path, index_col=0, header=0)['var_value']


def run_storage_model(initial_storage_level, temp_h, temp_c):
    data_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        './data/validation_data.csv')

    input_data = pd.read_csv(data_path, index_col=0, header=0)['var_value']

    u_value = calculate_storage_u_value(
        input_data['s_iso'],
        input_data['lamb_iso'],
        input_data['alpha_inside'],
        input_data['alpha_outside'])

    # Set up an energy system model
    periods = 10
    datetimeindex = pd.date_range('1/1/2019', periods=periods, freq='H')
    demand_timeseries = np.zeros(periods)
    heat_feedin_timeseries = np.zeros(periods)

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
        diameter=input_data['diameter'],
        height=input_data['height'],
        temp_h=temp_h,
        temp_c=temp_c,
        temp_env=input_data['temp_env'],
        u_value=u_value,  # W/(m2*K)
        min_storage_level=input_data['min_storage_level'],
        max_storage_level=input_data['max_storage_level'],
        initial_storage_level=initial_storage_level,
        capacity=input_data['maximum_heat_flow_charging'],
        efficiency=1,
        marginal_cost=0.0001
    )

    energysystem.add(
        bus_heat,
        heat_source,
        shortage,
        excess,
        heat_demand,
        thermal_storage)

    # create and solve the optimization model
    optimization_model = Model(energysystem)
    optimization_model.write('storage_model_facades.lp',
                             io_options={'symbolic_solver_labels': True})
    optimization_model.solve(solver='cbc', solve_kwargs={'tee': False})

    energysystem.results['main'] = solph.processing.results(optimization_model)
    string_results = solph.views.convert_keys_to_strings(energysystem.results['main'])

    # Get time series of level (state of charge) of the thermal energy storage
    TES_soc = (string_results['thermal_storage', 'None']['sequences'])

    # Save results to csv file
    TES_soc.to_csv("./data/storage_soc_calculated.csv")

    return


initial_storage_level = input_data['initial_storage_level']

run_storage_model(initial_storage_level=input_data['initial_storage_level'],
                  temp_h=input_data['temp_h'],
                  temp_c=input_data['temp_c'])

volume, surface = calculate_storage_dimensions(
    input_data['height'],
    input_data['diameter'])

# Max capacity in MWh
nominal_storage_capacity = calculate_capacities(
    volume,
    input_data['temp_h'],
    input_data['temp_c'])

# Get measurement data
filename = './data/storage_soc_measured.csv'
level_meas = pd.read_csv(filename, header=0)

# Get simulation results (hourly values)
filename = './data/storage_soc_calculated.csv'
TES_soc_df = pd.read_csv(filename, header=0)

# Convert to list
TES_soc_hourly = TES_soc_df['storage_content'].values

# Convert simulation data to relative values in %
TES_soc_relative = [soc / nominal_storage_capacity * 100 for soc in
                    TES_soc_hourly]

end_step = 7

# Make list with time steps for x-axes in plot
t_meas = np.arange(0, (len(level_meas) / 4), 0.25)

plt.style.use('ggplot')
fig, ax = plt.subplots()

# Plot horizontal line (initial level)
init_level = level_meas['level'][0]
plt.plot([init_level] * end_step, '--', color='gray')

# Plot simulation data
TES_soc_relative_list = [initial_storage_level * 100]
[TES_soc_relative_list.append(TES_soc_relative[i]) for i in range(10)]
plt.plot(TES_soc_relative_list[:end_step],
         label="storage level (simulation)")

# Plot measurement data
plt.plot(t_meas, level_meas['level'], label="storage level (measurement)")

plt.legend()
ax.set_xlabel("Time in h")
ax.set_ylabel("Storage level in %")
ax.set_xlim([0, 5.5])

ax.set_ylim([75, 80])

plt.savefig("validation.png")
