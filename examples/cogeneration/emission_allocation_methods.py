# -*- coding: utf-8

"""
Example on emission allocation in cogeneration.

"""

import pandas as pd
import matplotlib.pyplot as plt

from oemof.thermal.cogeneration import allocate_emissions


emissions_dict = {}

for method in ['iea', 'efficiency', 'finnish']:
    emissions_dict[method] = allocate_emissions(
        total_emissions=200,  # Arbitrary units. Assume [kgCO2].
        eta_el=0.3,
        eta_th=0.5,
        method=method,
        eta_el_ref=0.525,
        eta_th_ref=0.82
    )

df = pd.DataFrame(emissions_dict, index=['el', 'th']).T

print(df)

# Example plot
fig, ax = plt.subplots()
df.loc[:, 'el'] *= -1
bars = df.plot.barh(stacked=True, ax=ax)

for i, (el, th) in enumerate(zip(df['el'], df['th'])):
    ax.text(el, i, round(-el), ha='left')
    ax.text(th, i, round(th), ha='right')

ax.axvline(0)
ax.set_ylabel('Method')
ax.set_xlabel('Allocated emissions [kgCO2]')
plt.title('allocated to electricity', loc='left')
plt.title('allocated to heat', loc='right')
fig.tight_layout()
plt.show()
