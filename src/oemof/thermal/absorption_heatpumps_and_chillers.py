# -*- coding: utf-8

"""
This module is designed to hold functions for calculating absorption chillers.

This file is part of project oemof (github.com/oemof/oemof-thermal). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location:
oemof-thermal/src/oemof/thermal/stratified_thermal_storage.py

SPDX-License-Identifier: MIT
"""

def calc_characteristic_temp(t_hot, t_cool, t_chill, coef_a, coef_e, method):

    r"""
    Calculates the characteristic temperature difference.

    .. calc_characteristic_temp-equations:

    :math:`\Delta\Delta T = t_{G} - a \cdot t_{AC} + e \cdot t_{E}`

    Parameters
    ----------
    t_hot : numeric
        External arithmetic mean fluid temperature of hot water at heat exchanger (generator) [K]

    t_cool : numeric
        External arithmetic mean fluid temperature of cooling water at heat exchanger (absorber and condenser) [K]

    t_chill : numeric
        External arithmetic mean fluid temperature of chilled water at heat exchanger (evaporater) [K]

    coeff_a : numeric
        Characteristic parameter [-]

    coeff_e : numeric
        Characteristic parameter [-]

    method : string
        Method to calculate characteristic temperature difference

    Returns
    -------
    ddts : numeric
        Characteristic temperature difference [K]


    **Reference**


    [1] A. Kühn, C. Özgür-Popanda, and F. Ziegler,
    “A 10 kW indirectly fired absorption heat pump :
    Concepts for a reversible operation,”
    in Thermally driven heat pumps for heating and cooling,
    Universitätsverlag der TU Berlin, 2013, pp. 173–184.
    [http://nbn-resolving.de/urn:nbn:de:kobv:83-opus4-39458]

    [2] Maria Puig-Arnavat, Jesús López-Villada, \
    Joan Carles Bruno, Alberto Coronas.
    Analysis and parameter identification for characteristic equations \
    of single- and double-effect absorption chillers by means of \
    multivariable regression.
    In: International Journal of Refrigeration, 33 (2010) 70-78.
    """

    lengths = [len(t_hot), len(t_cool), len(t_chill)]
    length = max(lengths)

    # External mean temperature at generator (g)
    if len(t_hot) == 1:
        list_t_g = t_hot * length
    elif len(t_hot) == length:
        list_t_g = t_hot
    else:
        print("")
        print("ERROR - "
              "Length of argument 't_hot' seems not to match requirements")
    # External mean temperature at absorber/condenser (ac)
    if len(t_cool) == 1:
        list_t_ac = t_cool * length
    elif len(t_cool) == length:
        list_t_ac = t_cool
    else:
        print("")
        print("ERROR - "
              "Length of argument 't_cool' seems not to match requirements")
    # External mean temperature at evaporator (e)
    if len(t_chill) == 1:
        list_t_e = t_chill * length
    elif len(t_chill) == length:
        list_t_e = t_chill
    else:
        print("")
        print("ERROR - "
              "Length of argument 't_chill' seems not to match requirements")

    if method == 'kuehn_and_ziegler':
        ddts = [t_g - coef_a * t_ac + coef_e * t_e for
                t_g, t_ac, t_e in zip(list_t_g, list_t_ac, list_t_e)]
    else:
        ddts = None
        print("")
        print("ERROR - Unknown argument 'method'.")
        print("Possible options: 'kuehn_and_ziegler'")
        print("ddt was not calculated!")
        print("")

    return ddts


def calc_heat_flux(ddts, coef_s, coef_r, method):
    if method == 'kuehn_and_ziegler':
        Q_dots = [coef_s * ddt + coef_r for ddt in ddts]
    else:
        Q_dots = None
        print("ERROR - unknown argument 'method'. "
              "Heat flux Q_dot was not calculated!")
    return Q_dots


def define_AC_specs(Q_dots_evap, Q_dots_gen):
    # Define Absorption Chiller specifications
    AC_specs = {
        'COPs': [Q_e / Q_g for Q_e, Q_g in zip(Q_dots_evap, Q_dots_gen)],
        'Q_chill_max': [Q_e / max(Q_dots_evap) for Q_e in Q_dots_evap],  # In %
        'Q_chill_nominal': max(Q_dots_evap)  # Absolute value of max heat flux
    }
    return AC_specs
