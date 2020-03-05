

import oemof.thermal.absorption_heatpumps_and_chillers as abs_hp_chiller
import pandas as pd
import os
import matplotlib.pyplot as plt

filename = os.path.join(os.path.dirname(__file__),
                        'data/characteristic_parameters.csv')
charpara = pd.read_csv(filename)
print(charpara)
chiller_name = 'Broad_02'  # 'Kuehn, 'Rotartica', 'Safarik', 'Broad_02'

print(charpara[(charpara['name'] == chiller_name)]['a'].values[0])

# Delta Delta t
ddt = range(110, 157, 2)
print("Charateristic Temperatur Delta_Delta_t' =", ddt)

Q_dots_evap = abs_hp_chiller.calc_heat_flux(
    ddts=ddt,
    coef_s=charpara[(charpara['name'] == chiller_name)]['s_E'].values[0],
    coef_r=charpara[(charpara['name'] == chiller_name)]['r_E'].values[0],
    method='kuehn_and_ziegler'
)

Q_dots_gen = abs_hp_chiller.calc_heat_flux(
    ddts=ddt,
    coef_s=charpara[(charpara['name'] == chiller_name)]['s_G'].values[0],
    coef_r=charpara[(charpara['name'] == chiller_name)]['r_G'].values[0],
    method='kuehn_and_ziegler'
)

COPs = [Qevap / Qgen for Qgen, Qevap in zip(Q_dots_gen, Q_dots_evap)]

fig1 = plt.figure()
fig1.set_size_inches(8, 6, forward=True)
ax1 = fig1.add_subplot(111)
ax1.grid(axis='y')
line1 = ax1.plot(ddt,
                 Q_dots_gen,
                 linestyle=':',
                 color='black',
                 label='Driving Heat (Q_G)')
line2 = ax1.plot(ddt,
                 Q_dots_evap,
                 linestyle='--',
                 color='black',
                 label='Cooling Capacity (Q_E)')
plt.ylabel('Heat flow in kW')
ax2 = fig1.add_subplot(111, sharex=ax1, frameon=False)
line3 = ax2.plot(ddt,
                 COPs,
                 linestyle='',
                 marker='x',
                 color='black',
                 label='COP')
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position('right')
plt.ylabel('COP')
plt.xlabel(r'$\Delta\Delta t$ in K')
ax2.legend(loc='lower center')
ax1.legend(loc='lower left')

ax2.set_ylim(0, 1.6)
ax1.set_ylim(0, 1600)
ax1.set_xlim(100, 160)

plt.show()
