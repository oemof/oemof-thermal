"""
Example on how to use the 'calc_cops' function to get the
COPs of an imaginary air-source heat pump.

We use the ambient air as low temperature heat reservoir. The input is a
list to show how the function can be applied on several time steps. The output
is a list as well and may serve as input (conversion_factor) for a
oemof.solph.transformer.
"""

import compression_heatpumps_and_chillers as cmpr_hp_chiller

# Ambient temperatures in degC for a single day (24h)
temp_ambient = [2, 2, 3, 4, 4, 4,
                6, 6, 7, 7, 7, 8,
                8, 8, 7, 6, 5, 4,
                3, 2, 1, 0, -1, -1]

cops_airsource_hp = cmpr_hp_chiller.calc_cops(t_high=[35],
                                              t_low=temp_ambient,
                                              quality_grade=0.4,
                                              mode='heat_pump',
                                              consider_icing=True,
                                              factor_icing=0.8)


print("")
print("Coefficients of Performance (COP): ", *cops_airsource_hp, sep='\n')
print("")

