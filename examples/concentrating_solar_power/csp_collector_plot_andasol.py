"""
Example, which shows the difference between the new approach and a fix
efficiency.

The collectors efficiency and irradiance are calculated depending on
the loss method 'Andasol'.
"""
import os

import matplotlib.pyplot as plt
import pandas as pd

from oemof.thermal.concentrating_solar_power import csp_precalc

# Set paths
base_path = os.path.dirname(os.path.abspath(os.path.join(__file__)))
data_path = os.path.join(base_path, 'data')
results_path = os.path.join(base_path, 'results')

if not os.path.exists(results_path):
    os.mkdir(results_path)

# Precalculation

# Read input data
dataframe = pd.read_csv(os.path.join(data_path, 'data_Muscat_22_8.csv'))
dataframe['Datum'] = pd.to_datetime(dataframe['Datum'])
dataframe.set_index('Datum', inplace=True)
dataframe.index = dataframe.index.tz_localize(tz='Asia/Muscat')

df_temp_amb_series = pd.read_csv(os.path.join(data_path, 'data_Muscat_22_8_midday.csv'))
df_temp_amb_series['Datum'] = pd.to_datetime(df_temp_amb_series['Datum'])
df_temp_amb_series.set_index('Datum', inplace=True)
df_temp_amb_series.index = df_temp_amb_series.index.tz_localize(tz='Asia/Muscat')

temp_amb_series = pd.read_csv(os.path.join(data_path, 'temp_ambience.csv'))['t_amb']

# Parameters for the precalculation
periods = 24
latitude = 23.614328
longitude = 58.545284
timezone = 'Asia/Muscat'
collector_tilt = 10
collector_azimuth = 180
cleanliness = 0.9
a_1 = -8.65e-4
a_2 = 8.87e-4
a_3 = -5.425e-5
a_4 = 1.665e-6
a_5 = -2.309e-8
a_6 = 1.197e-10

eta_0 = 0.78
c_1 = 64
c_2 = 0
temp_collector_inlet = 435
temp_collector_outlet = 500

# Plot showing the difference between a constant efficiency without considering
# cleaniness for the heat of the collector during a day
data_precalc = csp_precalc(latitude, longitude,
                           collector_tilt, collector_azimuth, cleanliness,
                           eta_0, c_1, c_2,
                           temp_collector_inlet, temp_collector_outlet,
                           dataframe['t_amb'],
                           a_1, a_2, a_3, a_4, a_5, a_6,
                           loss_method='Andasol',
                           E_dir_hor=dataframe['E_dir_hor'])

heat_calc = data_precalc['collector_heat']
irradiance_on_collector = (data_precalc['collector_irradiance']
                           / (cleanliness**1.5))
heat_compare = irradiance_on_collector * eta_0
t = list(range(1, 25))

# Example plot
fig, ax = plt.subplots()
ax.plot(t, heat_calc, label='CSP precalculation')
ax.plot(t, heat_compare, label='constant efficiency')
ax.set(xlabel='time (h)', ylabel='Q_coll [W/m2]',
       title='Heat of the collector')
ax.grid()
ax.legend()

# Plot showing the difference between a constant efficiency and the efficiency
# depending on the ambient temperature for the same irradiance and hour of the
# day
df_result = pd.DataFrame()
for i in range(len(temp_amb_series)):
    df_temp_amb_series['t_amb'] = temp_amb_series[i]
    data_precalc_temp_amb = csp_precalc(
        latitude, longitude,
        collector_tilt, collector_azimuth, cleanliness,
        eta_0, c_1, c_2,
        temp_collector_inlet, temp_collector_outlet,
        df_temp_amb_series['t_amb'],
        a_1, a_2, a_3, a_4, a_5, a_6,
        loss_method='Andasol',
        E_dir_hor=df_temp_amb_series['E_dir_hor'])

    df_result = df_result.append(data_precalc_temp_amb, ignore_index=True)

fig, ax = plt.subplots()
ax.plot(temp_amb_series, df_result['eta_c'],
        label='efficiency depending on ambient temperature')
ax.plot(temp_amb_series, [eta_0] * 24, label='constant efficiency')
ax.set_ylim(0, 1)
ax.set(xlabel='ambient temperature [°C]', ylabel='eta_collector',
       title='collectors efficiency')
ax.grid()
ax.legend()
plt.show()
