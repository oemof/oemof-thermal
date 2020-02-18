.. _cogeneration_label:

~~~~~~~~~~~~
Cogeneration
~~~~~~~~~~~~

Scope
_____

The module is designed to hold functions that are helpful when modeling components that generate
more then one type of output.

Concept
_______

.. include:: ../src/oemof/thermal/cogeneration.py
  :start-after:  allocate_emissions-equations:
  :end-before: Reference

Usage
_____


.. code-block:: python

    em_el, em_heat = allocate_emissions(
            total_emissions=200,
            eta_el=0.3,
            eta_th=0.5,
            method=method,
            eta_el_ref=0.525,
            eta_th_ref=0.82
    )

.. 	image:: _pics/emission_allocation_methods.svg
   :width: 70 %
   :alt: emission_allocation_methods.svg
   :align: center