\* Source Pyomo model name=Model *\

min
objective:
+0 ONE_VAR_CONSTANT

s.t.

c_e_BusBlock_balance(bus_el_0)_:
+1 flow(bus_el_solar_collector_0)
= 0

c_e_BusBlock_balance(bus_el_1)_:
+1 flow(bus_el_solar_collector_1)
= 0

c_e_BusBlock_balance(bus_el_2)_:
+1 flow(bus_el_solar_collector_2)
= 0

c_e_BusBlock_balance(bus_heat_0)_:
+1 flow(solar_collector_bus_heat_0)
= 0

c_e_BusBlock_balance(bus_heat_1)_:
+1 flow(solar_collector_bus_heat_1)
= 0

c_e_BusBlock_balance(bus_heat_2)_:
+1 flow(solar_collector_bus_heat_2)
= 0

c_e_TransformerBlock_relation(solar_collector_bus_el_bus_heat_0)_:
+0.94999999999999996 flow(bus_el_solar_collector_0)
-0.019 flow(solar_collector_bus_heat_0)
= 0

c_e_TransformerBlock_relation(solar_collector_bus_el_bus_heat_1)_:
+0.94999999999999996 flow(bus_el_solar_collector_1)
-0.019 flow(solar_collector_bus_heat_1)
= 0

c_e_TransformerBlock_relation(solar_collector_bus_el_bus_heat_2)_:
+0.94999999999999996 flow(bus_el_solar_collector_2)
-0.019 flow(solar_collector_bus_heat_2)
= 0

c_e_TransformerBlock_relation(solar_collector_solar_collector_inflow_bus_heat_0)_:
-1 flow(solar_collector_bus_heat_0)
+0.94999999999999996 flow(solar_collector_inflow_solar_collector_0)
= 0

c_e_TransformerBlock_relation(solar_collector_solar_collector_inflow_bus_heat_1)_:
-1 flow(solar_collector_bus_heat_1)
+0.94999999999999996 flow(solar_collector_inflow_solar_collector_1)
= 0

c_e_TransformerBlock_relation(solar_collector_solar_collector_inflow_bus_heat_2)_:
-1 flow(solar_collector_bus_heat_2)
+0.94999999999999996 flow(solar_collector_inflow_solar_collector_2)
= 0

c_e_ONE_VAR_CONSTANT:
ONE_VAR_CONSTANT = 1.0

bounds
   0 <= flow(bus_el_solar_collector_0) <= +inf
   0 <= flow(bus_el_solar_collector_1) <= +inf
   0 <= flow(bus_el_solar_collector_2) <= +inf
   0 <= flow(solar_collector_bus_heat_0) <= +inf
   0 <= flow(solar_collector_bus_heat_1) <= +inf
   0 <= flow(solar_collector_bus_heat_2) <= +inf
   0 <= flow(solar_collector_inflow_solar_collector_0) <= 0
   0 <= flow(solar_collector_inflow_solar_collector_1) <= 14566.653922252568
   0 <= flow(solar_collector_inflow_solar_collector_2) <= 35868.680625337023
end
