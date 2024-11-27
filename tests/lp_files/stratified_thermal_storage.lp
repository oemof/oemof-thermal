\* Source Pyomo model name=Model *\

min 
objective:
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

c_e_GenericStorageBlock_losses(thermal_storage_0)_:
+0.00017659095910105282 GenericStorageBlock_storage_content(thermal_storage_0)
-1 GenericStorageBlock_storage_losses(thermal_storage_0)
= -0.028863382504856223

c_e_GenericStorageBlock_losses(thermal_storage_1)_:
+0.00017659095910105282 GenericStorageBlock_storage_content(thermal_storage_1)
-1 GenericStorageBlock_storage_losses(thermal_storage_1)
= -0.028863382504856223

c_e_GenericStorageBlock_losses(thermal_storage_2)_:
+0.00017659095910105282 GenericStorageBlock_storage_content(thermal_storage_2)
-1 GenericStorageBlock_storage_losses(thermal_storage_2)
= -0.028863382504856223

c_e_GenericStorageBlock_balance(thermal_storage_0)_:
+1 flow(bus_heat_thermal_storage_0)
-1 flow(thermal_storage_bus_heat_0)
+1 GenericStorageBlock_storage_content(thermal_storage_0)
-1 GenericStorageBlock_storage_content(thermal_storage_1)
-1 GenericStorageBlock_storage_losses(thermal_storage_0)
= 0

c_e_GenericStorageBlock_balance(thermal_storage_1)_:
+1 flow(bus_heat_thermal_storage_1)
-1 flow(thermal_storage_bus_heat_1)
+1 GenericStorageBlock_storage_content(thermal_storage_1)
-1 GenericStorageBlock_storage_content(thermal_storage_2)
-1 GenericStorageBlock_storage_losses(thermal_storage_1)
= 0

c_e_GenericStorageBlock_balance(thermal_storage_2)_:
+1 flow(bus_heat_thermal_storage_2)
-1 flow(thermal_storage_bus_heat_2)
+1 GenericStorageBlock_storage_content(thermal_storage_2)
-1 GenericStorageBlock_storage_content(thermal_storage_3)
-1 GenericStorageBlock_storage_losses(thermal_storage_2)
= 0

c_e_GenericStorageBlock_balanced_cstr(thermal_storage)_:
-1 GenericStorageBlock_storage_content(thermal_storage_0)
+1 GenericStorageBlock_storage_content(thermal_storage_3)
= 0

bounds
   0 <= flow(bus_heat_thermal_storage_0) <= 2
   0 <= flow(bus_heat_thermal_storage_1) <= 2
   0 <= flow(bus_heat_thermal_storage_2) <= 2
   0 <= flow(thermal_storage_bus_heat_0) <= 2
   0 <= flow(thermal_storage_bus_heat_1) <= 2
   0 <= flow(thermal_storage_bus_heat_2) <= 2
   91.06370721026974 <= GenericStorageBlock_storage_content(thermal_storage_0) <= 2.334966851545378
   91.06370721026974 <= GenericStorageBlock_storage_content(thermal_storage_1) <= 2.334966851545378
   91.06370721026974 <= GenericStorageBlock_storage_content(thermal_storage_2) <= 2.334966851545378
   91.06370721026974 <= GenericStorageBlock_storage_content(thermal_storage_3) <= 2.334966851545378
   -inf <= GenericStorageBlock_storage_losses(thermal_storage_0) <= +inf
   -inf <= GenericStorageBlock_storage_losses(thermal_storage_1) <= +inf
   -inf <= GenericStorageBlock_storage_losses(thermal_storage_2) <= +inf
end
