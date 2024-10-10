\* Source Pyomo model name=Model *\

min 
objective:
+50 InvestmentFlowBlock_invest(bus_heat_thermal_storage_0)
+0.0001 flow(thermal_storage_bus_heat_0)
+0.0001 flow(thermal_storage_bus_heat_1)
+0.0001 flow(thermal_storage_bus_heat_2)
+400 GenericInvestmentStorageBlock_invest(thermal_storage_0)

s.t.

c_e_BusBlock_balance(bus_heat_0)_:
-1 flow(bus_heat_thermal_storage_0)
+1 flow(thermal_storage_bus_heat_0)
= 0

c_e_BusBlock_balance(bus_heat_1)_:
-1 flow(bus_heat_thermal_storage_1)
+1 flow(thermal_storage_bus_heat_1)
= 0

c_e_BusBlock_balance(bus_heat_2)_:
-1 flow(bus_heat_thermal_storage_2)
+1 flow(thermal_storage_bus_heat_2)
= 0

c_e_InvestmentFlowBlock_total_rule(thermal_storage_bus_heat_0)_:
-1 InvestmentFlowBlock_invest(thermal_storage_bus_heat_0)
+1 InvestmentFlowBlock_total(thermal_storage_bus_heat_0)
= 0

c_e_InvestmentFlowBlock_total_rule(bus_heat_thermal_storage_0)_:
-1 InvestmentFlowBlock_invest(bus_heat_thermal_storage_0)
+1 InvestmentFlowBlock_total(bus_heat_thermal_storage_0)
= 0

c_u_InvestmentFlowBlock_max(thermal_storage_bus_heat_0_0)_:
+1 flow(thermal_storage_bus_heat_0)
-1 InvestmentFlowBlock_total(thermal_storage_bus_heat_0)
<= 0

c_u_InvestmentFlowBlock_max(thermal_storage_bus_heat_0_1)_:
+1 flow(thermal_storage_bus_heat_1)
-1 InvestmentFlowBlock_total(thermal_storage_bus_heat_0)
<= 0

c_u_InvestmentFlowBlock_max(thermal_storage_bus_heat_0_2)_:
+1 flow(thermal_storage_bus_heat_2)
-1 InvestmentFlowBlock_total(thermal_storage_bus_heat_0)
<= 0

c_u_InvestmentFlowBlock_max(bus_heat_thermal_storage_0_0)_:
+1 flow(bus_heat_thermal_storage_0)
-1 InvestmentFlowBlock_total(bus_heat_thermal_storage_0)
<= 0

c_u_InvestmentFlowBlock_max(bus_heat_thermal_storage_0_1)_:
+1 flow(bus_heat_thermal_storage_1)
-1 InvestmentFlowBlock_total(bus_heat_thermal_storage_0)
<= 0

c_u_InvestmentFlowBlock_max(bus_heat_thermal_storage_0_2)_:
+1 flow(bus_heat_thermal_storage_2)
-1 InvestmentFlowBlock_total(bus_heat_thermal_storage_0)
<= 0

c_e_GenericInvestmentStorageBlock_total_storage_rule(thermal_storage_0)_:
-1 GenericInvestmentStorageBlock_invest(thermal_storage_0)
+1 GenericInvestmentStorageBlock_total(thermal_storage_0)
= 0

c_u_GenericInvestmentStorageBlock_init_content_limit(thermal_storage)_:
-1 GenericInvestmentStorageBlock_invest(thermal_storage_0)
+1 GenericInvestmentStorageBlock_init_content(thermal_storage)
<= 0

c_e_GenericInvestmentStorageBlock_balance_first(thermal_storage)_:
-1 flow(bus_heat_thermal_storage_0)
+1 flow(thermal_storage_bus_heat_0)
+0.0002522727987158487 GenericInvestmentStorageBlock_invest(thermal_storage_0)
-0.999823409040899 GenericInvestmentStorageBlock_init_content(thermal_storage)
+1 GenericInvestmentStorageBlock_storage_content(thermal_storage_0)
= -0.005301437602932776

c_e_GenericInvestmentStorageBlock_balance(thermal_storage_0_1)_:
-1 flow(bus_heat_thermal_storage_1)
+1 flow(thermal_storage_bus_heat_1)
+0.0002522727987158487 GenericInvestmentStorageBlock_total(thermal_storage_0)
-0.999823409040899 GenericInvestmentStorageBlock_storage_content(thermal_storage_0)
+1 GenericInvestmentStorageBlock_storage_content(thermal_storage_1)
= -0.005301437602932776

c_e_GenericInvestmentStorageBlock_balance(thermal_storage_0_2)_:
-1 flow(bus_heat_thermal_storage_2)
+1 flow(thermal_storage_bus_heat_2)
+0.0002522727987158487 GenericInvestmentStorageBlock_total(thermal_storage_0)
-0.999823409040899 GenericInvestmentStorageBlock_storage_content(thermal_storage_1)
+1 GenericInvestmentStorageBlock_storage_content(thermal_storage_2)
= -0.005301437602932776

c_e_GenericInvestmentStorageBlock_balanced_cstr(thermal_storage)_:
-1 GenericInvestmentStorageBlock_init_content(thermal_storage)
+1 GenericInvestmentStorageBlock_storage_content(thermal_storage_2)
= 0

c_e_GenericInvestmentStorageBlock_power_coupled(thermal_storage_0)_:
+1 InvestmentFlowBlock_total(thermal_storage_bus_heat_0)
-1 InvestmentFlowBlock_total(bus_heat_thermal_storage_0)
= 0

c_u_GenericInvestmentStorageBlock_max_storage_content(thermal_storage_0_0)_:
-0.025 GenericInvestmentStorageBlock_total(thermal_storage_0)
+1 GenericInvestmentStorageBlock_storage_content(thermal_storage_0)
<= 0

c_u_GenericInvestmentStorageBlock_max_storage_content(thermal_storage_0_1)_:
-0.025 GenericInvestmentStorageBlock_total(thermal_storage_0)
+1 GenericInvestmentStorageBlock_storage_content(thermal_storage_1)
<= 0

c_u_GenericInvestmentStorageBlock_max_storage_content(thermal_storage_0_2)_:
-0.025 GenericInvestmentStorageBlock_total(thermal_storage_0)
+1 GenericInvestmentStorageBlock_storage_content(thermal_storage_2)
<= 0

c_u_GenericInvestmentStorageBlock_min_storage_content(thermal_storage_0_0)_:
+0.975 GenericInvestmentStorageBlock_total(thermal_storage_0)
-1 GenericInvestmentStorageBlock_storage_content(thermal_storage_0)
<= 0

c_u_GenericInvestmentStorageBlock_min_storage_content(thermal_storage_0_1)_:
+0.975 GenericInvestmentStorageBlock_total(thermal_storage_0)
-1 GenericInvestmentStorageBlock_storage_content(thermal_storage_1)
<= 0

c_u_GenericInvestmentStorageBlock_min_storage_content(thermal_storage_0_2)_:
+0.975 GenericInvestmentStorageBlock_total(thermal_storage_0)
-1 GenericInvestmentStorageBlock_storage_content(thermal_storage_2)
<= 0

bounds
   0 <= InvestmentFlowBlock_invest(thermal_storage_bus_heat_0) <= +inf
   0 <= InvestmentFlowBlock_invest(bus_heat_thermal_storage_0) <= +inf
   0 <= flow(bus_heat_thermal_storage_0) <= +inf
   0 <= flow(bus_heat_thermal_storage_1) <= +inf
   0 <= flow(bus_heat_thermal_storage_2) <= +inf
   0 <= flow(thermal_storage_bus_heat_0) <= +inf
   0 <= flow(thermal_storage_bus_heat_1) <= +inf
   0 <= flow(thermal_storage_bus_heat_2) <= +inf
   1 <= GenericInvestmentStorageBlock_invest(thermal_storage_0) <= +inf
   0 <= InvestmentFlowBlock_total(thermal_storage_bus_heat_0) <= +inf
   0 <= InvestmentFlowBlock_total(bus_heat_thermal_storage_0) <= +inf
   0 <= GenericInvestmentStorageBlock_total(thermal_storage_0) <= +inf
   0 <= GenericInvestmentStorageBlock_init_content(thermal_storage) <= +inf
   0 <= GenericInvestmentStorageBlock_storage_content(thermal_storage_0) <= +inf
   0 <= GenericInvestmentStorageBlock_storage_content(thermal_storage_1) <= +inf
   0 <= GenericInvestmentStorageBlock_storage_content(thermal_storage_2) <= +inf
end
