\* Source Pyomo model name=Model *\

min 
objective:
+1.743691139537028 GenericInvestmentStorageBlock_invest(storage)
+40 flow(backup_thermal_0)
+40 flow(backup_thermal_1)
+40 flow(backup_thermal_2)
+1000 flow(grid_electricity_0)
+1000 flow(grid_electricity_1)
+1000 flow(grid_electricity_2)

s.t.

c_e_Bus_balance(electricity_0)_:
-1 flow(electricity_solar_collector_0)
+1 flow(grid_electricity_0)
= 0

c_e_Bus_balance(electricity_1)_:
-1 flow(electricity_solar_collector_1)
+1 flow(grid_electricity_1)
= 0

c_e_Bus_balance(electricity_2)_:
-1 flow(electricity_solar_collector_2)
+1 flow(grid_electricity_2)
= 0

c_e_Bus_balance(thermal_0)_:
+1 flow(backup_thermal_0)
+1 flow(solar_collector_thermal_0)
+1 flow(storage_thermal_0)
-1 flow(thermal_collector_excess_heat_0)
-1 flow(thermal_storage_0)
= 61.916775007597408

c_e_Bus_balance(thermal_1)_:
+1 flow(backup_thermal_1)
+1 flow(solar_collector_thermal_1)
+1 flow(storage_thermal_1)
-1 flow(thermal_collector_excess_heat_1)
-1 flow(thermal_storage_1)
= 59.906213754316738

c_e_Bus_balance(thermal_2)_:
+1 flow(backup_thermal_2)
+1 flow(solar_collector_thermal_2)
+1 flow(storage_thermal_2)
-1 flow(thermal_collector_excess_heat_2)
-1 flow(thermal_storage_2)
= 56.346958718877602

c_u_GenericInvestmentStorageBlock_init_cap_limit(storage)_:
+1 GenericInvestmentStorageBlock_init_cap(storage)
-1 GenericInvestmentStorageBlock_invest(storage)
<= 0

c_e_GenericInvestmentStorageBlock_balance_first(storage)_:
+1 GenericInvestmentStorageBlock_capacity(storage_0)
-0.999 GenericInvestmentStorageBlock_init_cap(storage)
+1.0204081632653061 flow(storage_thermal_0)
-0.97999999999999998 flow(thermal_storage_0)
= 0

c_e_GenericInvestmentStorageBlock_balance(storage_1)_:
-0.999 GenericInvestmentStorageBlock_capacity(storage_0)
+1 GenericInvestmentStorageBlock_capacity(storage_1)
+1.0204081632653061 flow(storage_thermal_1)
-0.97999999999999998 flow(thermal_storage_1)
= 0

c_e_GenericInvestmentStorageBlock_balance(storage_2)_:
-0.999 GenericInvestmentStorageBlock_capacity(storage_1)
+1 GenericInvestmentStorageBlock_capacity(storage_2)
+1.0204081632653061 flow(storage_thermal_2)
-0.97999999999999998 flow(thermal_storage_2)
= 0

c_e_GenericInvestmentStorageBlock_balanced_cstr(storage)_:
+1 GenericInvestmentStorageBlock_capacity(storage_2)
-1 GenericInvestmentStorageBlock_init_cap(storage)
= 0

c_u_GenericInvestmentStorageBlock_max_capacity(storage_0)_:
+1 GenericInvestmentStorageBlock_capacity(storage_0)
-1 GenericInvestmentStorageBlock_invest(storage)
<= 0

c_u_GenericInvestmentStorageBlock_max_capacity(storage_1)_:
+1 GenericInvestmentStorageBlock_capacity(storage_1)
-1 GenericInvestmentStorageBlock_invest(storage)
<= 0

c_u_GenericInvestmentStorageBlock_max_capacity(storage_2)_:
+1 GenericInvestmentStorageBlock_capacity(storage_2)
-1 GenericInvestmentStorageBlock_invest(storage)
<= 0

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds
   0 <= flow(backup_thermal_0) <= +inf
   0 <= flow(backup_thermal_1) <= +inf
   0 <= flow(backup_thermal_2) <= +inf
   0 <= flow(electricity_solar_collector_0) <= +inf
   0 <= flow(electricity_solar_collector_1) <= +inf
   0 <= flow(electricity_solar_collector_2) <= +inf
   0 <= flow(grid_electricity_0) <= +inf
   0 <= flow(grid_electricity_1) <= +inf
   0 <= flow(grid_electricity_2) <= +inf
   0 <= flow(solar_collector_thermal_0) <= +inf
   0 <= flow(solar_collector_thermal_1) <= +inf
   0 <= flow(solar_collector_thermal_2) <= +inf
   0 <= flow(storage_thermal_0) <= +inf
   0 <= flow(storage_thermal_1) <= +inf
   0 <= flow(storage_thermal_2) <= +inf
   0 <= flow(thermal_collector_excess_heat_0) <= +inf
   0 <= flow(thermal_collector_excess_heat_1) <= +inf
   0 <= flow(thermal_collector_excess_heat_2) <= +inf
   0 <= flow(thermal_storage_0) <= +inf
   0 <= flow(thermal_storage_1) <= +inf
   0 <= flow(thermal_storage_2) <= +inf
   0 <= GenericInvestmentStorageBlock_capacity(storage_0) <= +inf
   0 <= GenericInvestmentStorageBlock_capacity(storage_1) <= +inf
   0 <= GenericInvestmentStorageBlock_capacity(storage_2) <= +inf
   0 <= GenericInvestmentStorageBlock_invest(storage) <= +inf
   0 <= GenericInvestmentStorageBlock_init_cap(storage) <= +inf
end
