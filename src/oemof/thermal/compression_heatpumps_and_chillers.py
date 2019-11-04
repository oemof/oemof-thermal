# -*- coding: utf-8 -

"""
This module provides functions to calculate compression heat pumps and
compression chillers.

This file is part of project oemof (github.com/oemof/oemof-thermal). It's
copyrighted by the contributors recorded in the version control history of the
file, available from its original location:
oemof-thermal/src/oemof/thermal/stratified_thermal_storage.py
"""



def calc_cops(t_high, t_low, quality_grade,
              consider_icing=False, factor_icing=None, mode=None):
    r"""
    Calculates the Coefficient of Performance (COP) of heat pumps and chillers.

    ====================== ======================== =======================
    math. symbol           attribute                explanation
    ====================== ======================== =======================
    :math:`T_{high}`       :py:obj:`t_high`         Temperature of the high temperature reservoir in degC
    :math:`T_{low}`        :py:obj:`low`            Temperature of the low temperature reservoir in degC
    :math:`q`              :py:obj:`quality_grade`  Quality grade
    ====================== ======================== =======================

    Note
    ----
    This is a note!

    Parameters
    ----------
    t_high : list of numerical values
        Temperature of the high temperature reservoir in degC
    t_low : list of numerical values
        Temperature of the low temperature reservoir in degC
    quality_grade:
        [0..1]
    consider_icing : boolean
        Activates a threshold-temperature.
        Below that temperature the COP drops. [True/False]
    factor_icing:
        Sets the relative COP drop caused by icing. [0..1]
    mode : string
        Two possible modes: "heat_pump" or "chiller"
    t_threshold:
        Temperature below which icing at heat exchanger occurs

    Returns
    -------
    cops : list of numerical values
        List of Coefficients of Performance (COPs)


    """
    # Expand length of lists with temperatures and convert unit to Kelvin.
    length = max([len(t_high), len(t_low)])
    if len(t_high) == 1:
        list_t_high_K = [t_high[0]+273.15]*length
    elif len(t_high) == length:
        list_t_high_K = [t+273.15 for t in t_high]
    if len(t_low) == 1:
        list_t_low_K = [t_low[0]+273.15]*length
    elif len(t_low) == length:
        list_t_low_K = [t+273.15 for t in t_low]

    # Calculate COPs depending on selected mode.
    if not consider_icing:
        if mode == "heat_pump":
            cops = [quality_grade * t_h/(t_h-t_l) for
                    t_h, t_l in zip(list_t_high_K, list_t_low_K)]
        elif mode == "chiller":
            cops = [quality_grade * t_l/(t_h-t_l) for
                    t_h, t_l in zip(list_t_high_K, list_t_low_K)]

    # Temperatures below 2 degC lead to icing at evaporator in
    # heat pumps working with ambient air as heat source.
    elif consider_icing:
        if mode == "heat_pump":
            cops = []
            for t_h, t_l in zip(list_t_high_K, list_t_low_K):
                if t_l < 2+273.15:
                    f_icing = factor_icing
                    cops = cops + [f_icing*quality_grade * t_h/(t_h-t_l)]
                if t_l >= 2+273.15:
                    cops = cops + [quality_grade * t_h / (t_h - t_l)]
        elif mode == "chiller":
            # Combining 'consider_icing' and mode 'chiller' is not possible!
            cops = None

    return cops


def calc_max_Q_dot_chill(nominal_conditions, cops):
    nominal_cop = (nominal_conditions['nominal_Q_chill'] /
                   nominal_conditions['nominal_el_consumption'])
    max_Q_chill=[actual_cop/nominal_cop for actual_cop in cops]
    print(nominal_cop)
    return max_Q_chill


def calc_max_Q_dot_heat(nominal_conditions, cops):
    nominal_cop = (nominal_conditions['nominal_Q_hot'] /
                   nominal_conditions['nominal_el_consumption'])
    max_Q_hot=[actual_cop/nominal_cop for actual_cop in cops]
    print(nominal_cop)
    return max_Q_hot


def calc_chiller_quality_grade(nominal_conditions):
    t_h = nominal_conditions['t_high_nominal']+273.15
    t_l =nominal_conditions['t_low_nominal']+273.15
    nominal_cop = (nominal_conditions['nominal_Q_chill'] /
                   nominal_conditions['nominal_el_consumption'])
    q_grade = nominal_cop / (t_l/(t_h-t_l))
    return q_grade
