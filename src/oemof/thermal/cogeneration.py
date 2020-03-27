# -*- coding: utf-8

"""
This module is designed to hold functions for pre- and postprocessing for combined heat
and power plants.

This file is part of project oemof (github.com/oemof/oemof-thermal). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location: oemof-thermal/src/oemof/thermal/chp.py

SPDX-License-Identifier: MIT
"""


def allocate_emissions(total_emissions, eta_el, eta_th, method, **kwargs):
    r"""
    Function to allocate emissions caused in cogeneration to the products electrical energy
    and heat according to specified method.

    .. allocate_emissions-equations:

    **IEA method**

    :math:`EM_{el} = EM \cdot \frac{\eta_{el}}{\eta_{el} + \eta_{th}}`,

    :math:`EM_{th} = EM \cdot \frac{\eta_{th}}{\eta_{el} + \eta_{th}}`.

    **Efficiency method**

    :math:`EM_{el} = EM \cdot \frac{\eta_{th}}{\eta_{el} + \eta_{th}}`,

    :math:`EM_{th} = EM \cdot \frac{\eta_{el}}{\eta_{el} + \eta_{th}}`.

    **Finnish method**

    :math:`EM_{el} = EM \cdot (1-PEE)\frac{\eta_{el}}{\eta_{el,REF}}`,

    :math:`EM_{th} = EM \cdot (1-PEE)\frac{\eta_{th}}{\eta_{th,REF}}`,

    with

    :math:`PEE = 1 - \frac{1}{\frac{\eta_{th}}{\eta_{th,ref}}+\frac{\eta_{el}}{\eta_{el,ref}}}`.

    Reference:
    Mauch, W., Corradini, R., Wiesmeyer, K., Schwentzek, M. (2010).
    Allokationsmethoden für spezifische CO2-Emissionen von Strom und Waerme aus KWK-Anlagen.
    Energiewirtschaftliche Tagesfragen, 55(9), 12–14.

    Parameters
    ----------
    total_emissions : numeric
        Total absolute emissions to be allocated to electricity and heat [in CO2 equivalents].

    eta_el : numeric
        Electrical efficiency of the cogeneration [-].

    eta_th : numeric
        Thermal efficiency of the cogeneration [-].

    method : str
        Specification of method to use. Choose from ['iea', finnish', 'efficiency'].

    **kwargs
        For the finnish method, `eta_el_ref` and `eta_th_ref` have to be passed.

    Returns
    -------
    allocated_emissions_electricity : numeric
        total emissions allocated to electricity according to specified `method`
        [in CO2 equivalents].

    allocated_emissions_heat : numeric
            total emissions allocated to heat according to specified `method`
            [in CO2 equivalents].

    """
    if method == 'iea':
        allocated_emissions_electricity = total_emissions * eta_el * 1 / (eta_el + eta_th)
        allocated_emissions_heat = total_emissions * eta_th * 1 / (eta_el + eta_th)

    elif method == 'efficiency':
        allocated_emissions_electricity = total_emissions * eta_th * 1 / (eta_el + eta_th)
        allocated_emissions_heat = total_emissions * eta_el * 1 / (eta_el + eta_th)

    elif method == 'finnish':
        if kwargs is not None and kwargs.keys() >= {'eta_el_ref', 'eta_th_ref'}:
            eta_el_ref = kwargs.get('eta_el_ref')
            eta_th_ref = kwargs.get('eta_th_ref')
        else:
            raise ValueError('Must specify eta_el_ref, eta_th_ref when using finnish method.')

        pee = 1 - 1 / ((eta_el / eta_el_ref) + (eta_th / eta_th_ref))
        allocated_emissions_electricity = total_emissions * (1 - pee) * (eta_el / eta_el_ref)
        allocated_emissions_heat = total_emissions * (1 - pee) * (eta_th / eta_th_ref)

    else:
        raise ValueError(f"Method '{method}' is not available. "
                         "Please choose from ['iea', finnish', 'efficiency']")

    return allocated_emissions_electricity, allocated_emissions_heat
