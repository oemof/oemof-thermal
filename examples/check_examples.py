from absorption_heatpump_and_chiller.absorption_chiller import (
    absorption_chiller_exaple,
)
from absorption_heatpump_and_chiller.cooling_cap_dependence_on_cooling_water_temp import (
    cooling_cap_example,
)
from cogeneration.emission_allocation_methods import (
    emission_allocation_example,
)
from compression_heatpump_and_chiller.airsource_heatpump_const_max_output import (
    airource_hp_const_example,
)
from compression_heatpump_and_chiller.airsource_heatpump_variable_max_output import (
    airource_hp_variable_example,
)
from compression_heatpump_and_chiller.chiller_cop import (
    chiller_cop_const_example,
)
from compression_heatpump_and_chiller.chiller_cop_as_TimeSeries import (
    chiller_cop_timeseries_example,
)
from compression_heatpump_and_chiller.groundsource_heatpump import (
    groundsource_hp_example,
)
from concentrating_solar_power.csp_collector_plot import csp_collector_example
from concentrating_solar_power.csp_collector_plot_andasol import (
    csp_andasol_example,
)
from concentrating_solar_power.csp_facade import csp_facade_example
from concentrating_solar_power.csp_plant import csp_plant_example
from solar_thermal_collector.flat_plate_collector import (
    flat_plate_collector_example,
)
from solar_thermal_collector.flat_plate_collector_facade import (
    flat_plate_collector_facade_example,
)
from solar_thermal_collector.flat_plate_collector_investment import (
    flat_plate_collector_investment_example,
)
from stratified_thermal_storage.investment_fixed_ratio_facade import (
    fixed_ratio_invest_facade_example,
)
from stratified_thermal_storage.investment_fixed_ratio_generic_storage import (
    fixed_ratio_invest_example,
)
from stratified_thermal_storage.investment_independent_facade import (
    invest_independent_facade_example,
)
from stratified_thermal_storage.investment_independent_generic_storage import (
    invest_independent_example,
)
from stratified_thermal_storage.operation_facade import (
    operation_facade_example,
)
from stratified_thermal_storage.operation_generic_storage import (
    operation_example,
)

# absorption_chiller_example()
cooling_cap_example()

emission_allocation_example()

airource_hp_const_example()
airource_hp_variable_example()
chiller_cop_const_example()
chiller_cop_timeseries_example()
groundsource_hp_example()

csp_collector_example()
csp_andasol_example()
csp_facade_example()
csp_plant_example()

flat_plate_collector_example()
flat_plate_collector_facade_example()
flat_plate_collector_investment_example()

operation_example()
operation_facade_example()
fixed_ratio_invest_facade_example()
fixed_ratio_invest_example()
invest_independent_facade_example()
invest_independent_example()
