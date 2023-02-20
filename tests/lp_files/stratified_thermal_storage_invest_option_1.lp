\* Source Pyomo model name=Model *\

min
objective:
+400 GenericInvestmentStorageBlock_invest(thermal_storage)
+0.0001 flow(thermal_storage_bus_heat_0)
+0.0001 flow(thermal_storage_bus_heat_1)
+0.0001 flow(thermal_storage_bus_heat_2)

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

c_u_InvestmentFlowBlock_max(bus_heat_thermal_storage_0)_:
-1 InvestmentFlowBlock_invest(bus_heat_thermal_storage)
+1 flow(bus_heat_thermal_storage_0)
<= 0

c_u_InvestmentFlowBlock_max(bus_heat_thermal_storage_1)_:
-1 InvestmentFlowBlock_invest(bus_heat_thermal_storage)
+1 flow(bus_heat_thermal_storage_1)
<= 0

c_u_InvestmentFlowBlock_max(bus_heat_thermal_storage_2)_:
-1 InvestmentFlowBlock_invest(bus_heat_thermal_storage)
+1 flow(bus_heat_thermal_storage_2)
<= 0

c_u_InvestmentFlowBlock_max(thermal_storage_bus_heat_0)_:
-1 InvestmentFlowBlock_invest(thermal_storage_bus_heat)
+1 flow(thermal_storage_bus_heat_0)
<= 0

c_u_InvestmentFlowBlock_max(thermal_storage_bus_heat_1)_:
-1 InvestmentFlowBlock_invest(thermal_storage_bus_heat)
+1 flow(thermal_storage_bus_heat_1)
<= 0

c_u_InvestmentFlowBlock_max(thermal_storage_bus_heat_2)_:
-1 InvestmentFlowBlock_invest(thermal_storage_bus_heat)
+1 flow(thermal_storage_bus_heat_2)
<= 0

c_u_GenericInvestmentStorageBlock_init_content_limit(thermal_storage)_:
+1 GenericInvestmentStorageBlock_init_content(thermal_storage)
-1 GenericInvestmentStorageBlock_invest(thermal_storage)
<= 0

c_e_GenericInvestmentStorageBlock_balance_first(thermal_storage)_:
+0.99982340904089895 GenericInvestmentStorageBlock_init_content(thermal_storage)
-0.00025227279871584872 GenericInvestmentStorageBlock_invest(thermal_storage)
-1 GenericInvestmentStorageBlock_storage_content(thermal_storage_0)
+1 flow(bus_heat_thermal_storage_0)
-1 flow(thermal_storage_bus_heat_0)
= 0.0053014376029327757

c_e_GenericInvestmentStorageBlock_balance(thermal_storage_1)_:
-0.00025227279871584872 GenericInvestmentStorageBlock_invest(thermal_storage)
+0.99982340904089895 GenericInvestmentStorageBlock_storage_content(thermal_storage_0)
-1 GenericInvestmentStorageBlock_storage_content(thermal_storage_1)
+1 flow(bus_heat_thermal_storage_1)
-1 flow(thermal_storage_bus_heat_1)
= 0.0053014376029327757

c_e_GenericInvestmentStorageBlock_balance(thermal_storage_2)_:
-0.00025227279871584872 GenericInvestmentStorageBlock_invest(thermal_storage)
+0.99982340904089895 GenericInvestmentStorageBlock_storage_content(thermal_storage_1)
-1 GenericInvestmentStorageBlock_storage_content(thermal_storage_2)
+1 flow(bus_heat_thermal_storage_2)
-1 flow(thermal_storage_bus_heat_2)
= 0.0053014376029327757

c_e_GenericInvestmentStorageBlock_balanced_cstr(thermal_storage)_:
-1 GenericInvestmentStorageBlock_init_content(thermal_storage)
+1 GenericInvestmentStorageBlock_storage_content(thermal_storage_2)
= 0

c_e_GenericInvestmentStorageBlock_power_coupled(thermal_storage)_:
-1 InvestmentFlowBlock_invest(bus_heat_thermal_storage)
+1 InvestmentFlowBlock_invest(thermal_storage_bus_heat)
= 0

c_e_GenericInvestmentStorageBlock_storage_capacity_inflow(thermal_storage)_:
-0.16666666666666666 GenericInvestmentStorageBlock_invest(thermal_storage)
+1 InvestmentFlowBlock_invest(bus_heat_thermal_storage)
= 0

c_u_GenericInvestmentStorageBlock_max_storage_content(thermal_storage_0)_:
-0.025000000000000001 GenericInvestmentStorageBlock_invest(thermal_storage)
+1 GenericInvestmentStorageBlock_storage_content(thermal_storage_0)
<= 0

c_u_GenericInvestmentStorageBlock_max_storage_content(thermal_storage_1)_:
-0.025000000000000001 GenericInvestmentStorageBlock_invest(thermal_storage)
+1 GenericInvestmentStorageBlock_storage_content(thermal_storage_1)
<= 0

c_u_GenericInvestmentStorageBlock_max_storage_content(thermal_storage_2)_:
-0.025000000000000001 GenericInvestmentStorageBlock_invest(thermal_storage)
+1 GenericInvestmentStorageBlock_storage_content(thermal_storage_2)
<= 0

c_u_GenericInvestmentStorageBlock_min_storage_content(thermal_storage_0)_:
+0.97499999999999998 GenericInvestmentStorageBlock_invest(thermal_storage)
-1 GenericInvestmentStorageBlock_storage_content(thermal_storage_0)
<= 0

c_u_GenericInvestmentStorageBlock_min_storage_content(thermal_storage_1)_:
+0.97499999999999998 GenericInvestmentStorageBlock_invest(thermal_storage)
-1 GenericInvestmentStorageBlock_storage_content(thermal_storage_1)
<= 0

c_u_GenericInvestmentStorageBlock_min_storage_content(thermal_storage_2)_:
+0.97499999999999998 GenericInvestmentStorageBlock_invest(thermal_storage)
-1 GenericInvestmentStorageBlock_storage_content(thermal_storage_2)
<= 0

c_e_ONE_VAR_CONSTANT:
ONE_VAR_CONSTANT = 1.0

bounds
   0 <= flow(bus_heat_thermal_storage_0) <= +inf
   0 <= flow(bus_heat_thermal_storage_1) <= +inf
   0 <= flow(bus_heat_thermal_storage_2) <= +inf
   0 <= flow(thermal_storage_bus_heat_0) <= +inf
   0 <= flow(thermal_storage_bus_heat_1) <= +inf
   0 <= flow(thermal_storage_bus_heat_2) <= +inf
   0 <= InvestmentFlowBlock_invest(bus_heat_thermal_storage) <= +inf
   0 <= InvestmentFlowBlock_invest(thermal_storage_bus_heat) <= +inf
   0 <= GenericInvestmentStorageBlock_storage_content(thermal_storage_0) <= +inf
   0 <= GenericInvestmentStorageBlock_storage_content(thermal_storage_1) <= +inf
   0 <= GenericInvestmentStorageBlock_storage_content(thermal_storage_2) <= +inf
   1 <= GenericInvestmentStorageBlock_invest(thermal_storage) <= +inf
   0 <= GenericInvestmentStorageBlock_init_content(thermal_storage) <= +inf
end