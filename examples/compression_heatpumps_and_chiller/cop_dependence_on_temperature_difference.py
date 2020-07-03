"""
Example on how to use the 'calc_cops' function to get the
COPs of a heat pump.

This example plots the temperature dependency of the COP.
"""

import oemof.thermal.compression_heatpumps_and_chillers as cmpr_hp_chiller
import pandas as pd
import matplotlib.pyplot as plt

# Sink temperature
temp_high = 65
temp_high_industrial = 110

# Delta t
temp_difference = range(10, 71, 1)
temp_difference_industrial = range(20, 142, 2)
temperature_diff_q_grade = range(5, 147, 2)

# Quality grades
quality_grades = [q / 10 for q in range(2, 11, 2)]

cops = pd.DataFrame()

# COPs of ax exemplary heat pump for domestic hot water
# (sink temperature below 100 degC)
cops['temperature_difference'] = temp_difference
list_temp_low = [temp_high - temp_diff for temp_diff in temp_difference]
cops[temp_high] = cmpr_hp_chiller.calc_cops(
    temp_high=[temp_high],
    temp_low=list_temp_low,
    quality_grade=0.35,
    mode='heat_pump')

# COPs of ax exemplary hight temperature heat pump for industrial applications
# (sink temperature above 100 degC and higher quality grade)
cops['temperature_difference_industrial'] = temp_difference_industrial
temp_l_ind = [temp_high_industrial - temp_diff for
              temp_diff in temp_difference_industrial]
cops[temp_high_industrial] = cmpr_hp_chiller.calc_cops(
    temp_high=[temp_high_industrial],
    temp_low=temp_l_ind,
    quality_grade=0.45,
    mode='heat_pump')

# COPs for varying quality grades
cops_q_grade = pd.DataFrame()
cops_q_grade['temperature_diff'] = temperature_diff_q_grade
list_temp_low_q_grade = [temp_high - temp_diff_q for
                         temp_diff_q in temperature_diff_q_grade]
for q in quality_grades:
    list_temp_low = [temp_high - temp_diff_q for
                     temp_diff_q in temperature_diff_q_grade]
    cops_q_grade[q] = cmpr_hp_chiller.calc_cops(
        temp_high=[temp_high],
        temp_low=list_temp_low_q_grade,
        quality_grade=q,
        mode='heat_pump')

# Example plot
fig1 = plt.figure(figsize=(8, 6))
fig1.set_size_inches(8, 6, forward=True)
axs = fig1.add_subplot(111)
plt.plot(cops['temperature_difference_industrial'],
         cops[temp_high_industrial],
         linestyle='-',
         color='red',
         label='COP of a high temperature heat pump')
plt.plot(cops['temperature_difference'],
         cops[temp_high],
         linestyle='-',
         color='blue',
         label='COP of a heat pump for domestic hot water')

for q in quality_grades:
    plt.plot(cops_q_grade['temperature_diff'],
             cops_q_grade[q],
             linestyle='dotted',
             color='grey')
axs.set_ylim(0, 12)
axs.set_xlim(0, 145)
plt.title('COP Dependence on Temperature Difference')
plt.xlabel('Temperature Difference in K')
plt.ylabel('Coefficient of Performance (COP)')
plt.legend(loc='upper right')
bbox_props = dict(boxstyle="round", fc="w", ec="1.0", alpha=0.9)
textcol = '0.3'
textsize = 10
axs.text(47, 7.2, "100%",
         ha="center",
         va="center",
         size=textsize,
         rotation=-60,
         color=textcol,
         bbox=bbox_props)
axs.text(57, 5.85, "(Carnot)",
         ha="center",
         va="center",
         size=textsize,
         rotation=-52,
         color=textcol,
         bbox=bbox_props)
axs.text(30, 9.1, "quality grade",
         ha="center",
         va="center",
         size=textsize,
         rotation=-76,
         color=textcol,
         bbox=bbox_props)
axs.text(39, 6.8, "80%",
         ha="center",
         va="center",
         size=textsize,
         rotation=-70,
         color=textcol,
         bbox=bbox_props)
axs.text(12, 5.7, "20%",
         ha="center",
         va="center",
         size=textsize,
         rotation=-70,
         color=textcol,
         bbox=bbox_props)
axs.annotate('quality grade 45%,\nT_sink 110 degC',
             xy=(97, 1.8),
             xytext=(95, 4),
             arrowprops=dict(arrowstyle="->",
                             connectionstyle="arc3"))
axs.annotate('quality grade 35%,\nT_sink 65 degC',
             xy=(40, 3),
             xytext=(4, 0.6),
             arrowprops=dict(arrowstyle="->",
                             connectionstyle="arc3"))

# plt.savefig('cop_dependence_on_temp_difference.png', dpi=300)
plt.show()
print("")
