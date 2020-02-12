"""
Example on how to use the 'calc_cops' function to get the
COPs of a compression chiller using pd.Time-Series as input.

We use the ambient air as heat sink (high temperature reservoir). The input is
a list to show how the function can be applied on several time steps. The
output is a list as well and may serve as input (conversion_factor) for a
oemof.solph.transformer.
"""

import oemof.thermal.compression_heatpumps_and_chillers as cmpr_hp_chiller
import pandas as pd

# Ambient temperatures in degC for a single day (24h)
temp_ambient = [24, 24, 24, 25, 25, 25,
                26, 27, 28, 29, 31, 32,
                35, 34, 27, 26, 25, 24,
                24, 24, 24, 24, 24, 23]

timestamps = pd.date_range('20200101', periods=24, freq='H')

df_hour = pd.DataFrame(temp_ambient, timestamps)
series_hour = pd.Series(temp_ambient, timestamps)
print(df_hour)
print("")
print(series_hour)

cops_chiller = cmpr_hp_chiller.calc_cops(temp_high=series_hour,
                                         temp_low=[18],
                                         quality_grade=0.3,
                                         mode='chiller')


print("")
print("Coefficients of Performance (COP):")
t = 1
for cop_chiller in cops_chiller:
    print(t, "h: {:2.2f}".format(cop_chiller))
    t += 1
print("")
