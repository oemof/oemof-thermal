"""
Example on how to use the 'calc_cops' function to get the
COPs of a compression chiller.

We use the ambient air as heat sink (high temperature reservoir). The input is
a list to show how the function can be applied on several time steps. The
output is a list as well and may serve as input (conversion_factor) for a
oemof.solph.transformer.
"""

import compression_heatpumps_and_chillers as cmpr_hp_chiller

# Ambient temperatures in degC for a single day (24h)
temp_ambient = [24, 24, 24, 25, 25, 25,
                26, 27, 28, 29, 31, 32,
                35, 34, 27, 26, 25, 24,
                24, 24, 24, 24, 24, 23]

cops_chiller = cmpr_hp_chiller.calc_cops(t_high=temp_ambient,
                                         t_low=[18],
                                         quality_grade=0.3,
                                         mode='chiller')


print("")
print("Coefficients of Performance (COP): ", *cops_chiller, sep='\n')
print("")

