
import oemof.thermal.absorption_heatpumps_and_chillers as abs_hp_chiller
import matplotlib.pyplot as plt
import os
import pandas as pd

filename = os.path.join(os.path.dirname(__file__),
                        'data/characteristic_parameters.csv')
charpara = pd.read_csv(filename)
chiller_name = 'Kuehn'

t_cooling = [23, 25, 27, 29, 31, 33, 35, 36, 37, 38, 39, 40]

ddt_75 = abs_hp_chiller.calc_characteristic_temp(
    t_hot=[75],
    t_cool=t_cooling,
    t_chill=[15],
    coef_a=charpara[(charpara['name'] == chiller_name)]['a'].values[0],
    coef_e=charpara[(charpara['name'] == chiller_name)]['e'].values[0],
    method='kuehn_and_ziegler')
Q_dots_evap_75 = abs_hp_chiller.calc_heat_flux(
    ddts=ddt_75,
    coef_s=charpara[(charpara['name'] == chiller_name)]['s_E'].values[0],
    coef_r=charpara[(charpara['name'] == chiller_name)]['r_E'].values[0],
    method='kuehn_and_ziegler')
Q_dots_gen_75 = abs_hp_chiller.calc_heat_flux(
    ddts=ddt_75,
    coef_s=charpara[(charpara['name'] == chiller_name)]['s_G'].values[0],
    coef_r=charpara[(charpara['name'] == chiller_name)]['r_G'].values[0],
    method='kuehn_and_ziegler')
COPs_75 = [Qevap / Qgen for Qgen, Qevap in zip(Q_dots_gen_75, Q_dots_evap_75)]

ddt_80 = abs_hp_chiller.calc_characteristic_temp(
    t_hot=[80],
    t_cool=t_cooling,
    t_chill=[15],
    coef_a=charpara[(charpara['name'] == chiller_name)]['a'].values[0],
    coef_e=charpara[(charpara['name'] == chiller_name)]['e'].values[0],
    method='kuehn_and_ziegler')
Q_dots_evap_80 = abs_hp_chiller.calc_heat_flux(
    ddts=ddt_80,
    coef_s=charpara[(charpara['name'] == chiller_name)]['s_E'].values[0],
    coef_r=charpara[(charpara['name'] == chiller_name)]['r_E'].values[0],
    method='kuehn_and_ziegler')


fig1 = plt.figure(figsize=(8, 6))
fig1.set_size_inches(8, 6, forward=True)
ax1 = fig1.add_subplot(111)
ax1.grid(axis='y')

line1 = ax1.plot(t_cooling,
                 Q_dots_evap_80,
                 linestyle='dotted',
                 marker='d',
                 color='black',
                 label='Cooling capacity ($80°$C driving heat)')
line2 = ax1.plot(t_cooling,
                 Q_dots_evap_75,
                 linestyle='dashed',
                 marker='d',
                 color='black',
                 label='Cooling capacity ($75°$C driving heat)')
plt.ylabel('Cooling capacity in kW')
ax2 = fig1.add_subplot(111, sharex=ax1, frameon=False)
line3 = ax2.plot(t_cooling,
                 COPs_75,
                 linestyle='-',
                 marker='o',
                 color='black',
                 label='COP ($75°$C driving heat)')
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position('right')
plt.ylabel('COP')
plt.xlabel('Cooling water temperature in $°$C')
plt.title('Chiller performance at varying cooling water temperatures')
ax2.legend(loc='upper right')
ax1.legend(loc='lower left')

ax2.set_ylim(0.4, 0.8)
ax1.set_ylim(0, 24)
ax1.set_xlim(20, 43)

plt.show()
