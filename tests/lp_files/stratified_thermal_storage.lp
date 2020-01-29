\* Source Pyomo model name=Model *\

min
objective:
+0.0001 flow(thermal_storage_bus_heat_0)
+0.0001 flow(thermal_storage_bus_heat_1)
+0.0001 flow(thermal_storage_bus_heat_2)

s.t.

c_e_Bus_balance(bus_heat_0)_:
-1 flow(bus_heat_thermal_storage_0)
+1 flow(thermal_storage_bus_heat_0)
= 0

c_e_Bus_balance(bus_heat_1)_:
-1 flow(bus_heat_thermal_storage_1)
+1 flow(thermal_storage_bus_heat_1)
= 0

c_e_Bus_balance(bus_heat_2)_:
-1 flow(bus_heat_thermal_storage_2)
+1 flow(thermal_storage_bus_heat_2)
= 0

c_e_GenericStorageBlock_balance_first(thermal_storage)_:
+1 GenericStorageBlock_capacity(thermal_storage_0)
-0.99982274917797465 GenericStorageBlock_init_cap(thermal_storage)
-1 flow(bus_heat_thermal_storage_0)
+1 flow(thermal_storage_bus_heat_0)
= -0.028949190751205309

c_e_GenericStorageBlock_balance(thermal_storage_1)_:
-0.99982274917797465 GenericStorageBlock_capacity(thermal_storage_0)
+1 GenericStorageBlock_capacity(thermal_storage_1)
-1 flow(bus_heat_thermal_storage_1)
+1 flow(thermal_storage_bus_heat_1)
= -0.028949190751205309

c_e_GenericStorageBlock_balance(thermal_storage_2)_:
-0.99982274917797465 GenericStorageBlock_capacity(thermal_storage_1)
+1 GenericStorageBlock_capacity(thermal_storage_2)
-1 flow(bus_heat_thermal_storage_2)
+1 flow(thermal_storage_bus_heat_2)
= -0.028949190751205309

c_e_GenericStorageBlock_balanced_cstr(thermal_storage)_:
+1 GenericStorageBlock_capacity(thermal_storage_2)
-1 GenericStorageBlock_init_cap(thermal_storage)
= 0

c_e_ONE_VAR_CONSTANT:
ONE_VAR_CONSTANT = 1.0

bounds
   0 <= flow(bus_heat_thermal_storage_0) <= 2
   0 <= flow(bus_heat_thermal_storage_1) <= 2
   0 <= flow(bus_heat_thermal_storage_2) <= 2
   0 <= flow(thermal_storage_bus_heat_0) <= 2
   0 <= flow(thermal_storage_bus_heat_1) <= 2
   0 <= flow(thermal_storage_bus_heat_2) <= 2
   91.05510112326489 <= GenericStorageBlock_capacity(thermal_storage_0) <= 2.3347461826478177
   91.05510112326489 <= GenericStorageBlock_capacity(thermal_storage_1) <= 2.3347461826478177
   91.05510112326489 <= GenericStorageBlock_capacity(thermal_storage_2) <= 2.3347461826478177
   0 <= GenericStorageBlock_init_cap(thermal_storage) <= 93.38984730591271
end
