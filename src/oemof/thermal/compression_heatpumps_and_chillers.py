# -*- coding: utf-8

"""
This module provides functions to calculate compression heat pumps and
compression chillers.

This file is part of project oemof (github.com/oemof/oemof-thermal). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location:
oemof-thermal/src/oemof/thermal/compression_heatpumps_and_chillers.py

SPDX-License-Identifier: MIT
"""
import pandas as pd


def calc_cops(mode, temp_high, temp_low, quality_grade, temp_threshold_icing=2,
              factor_icing=None):

    r"""
    Calculates the Coefficient of Performance (COP) of heat pumps and chillers
    based on the Carnot efficiency (ideal process) and a scale-down factor.

    Note
    ----
    Applications of air-source heat pumps should consider icing
    at the heat exchanger at air-temperatures around :math:`2^\circ C` .
    Icing causes a reduction of the efficiency.

    .. calc_cops-equations:

        mode='heat_pump'

        :math:`COP = \eta \cdot \frac{T_\mathrm{high}}{T_\mathrm{high}
        - T_\mathrm{low}}`

        :math:`COP = f_\mathrm{icing} \cdot\eta
        \cdot\frac{T_\mathrm{high}}{T_\mathrm{high} - T_\mathrm{low}}`

        mode='chiller'

        :math:`COP = \eta \cdot \frac{T_\mathrm{low}}{T_\mathrm{high}
        - T_\mathrm{low}}`

    Parameters
    ----------
    temp_high : list or pandas.Series of numerical values
        Temperature of the high temperature reservoir in :math:`^\circ C`
    temp_low : list or pandas.Series of numerical values
        Temperature of the low temperature reservoir in :math:`^\circ C`
    quality_grade : numerical value
        Factor that scales down the efficiency of the real heat pump
        (or chiller) process from the ideal process (Carnot efficiency), where
         a factor of 1 means teh real process is equal to the ideal one.
    factor_icing: numerical value
        Sets the relative COP drop caused by icing, where 1 stands for no
        efficiency-drop.
    mode : string
        Two possible modes: "heat_pump" or "chiller" (default 'None')
    t_threshold:
        Temperature in :math:`^\circ C` below which icing at heat exchanger
        occurs (default 2)

    Returns
    -------
    cops : list of numerical values
        List of Coefficients of Performance (COPs)


    """
    # Check if input arguments have proper type and length
    if not isinstance(temp_low, (list, pd.Series)):
        raise TypeError("Argument 'temp_low' is not of type list or pd.Series!")

    if not isinstance(temp_high, (list, pd.Series)):
        raise TypeError("Argument 'temp_high' is not of "
                        "type list or pd.Series!")

    if len(temp_high) != len(temp_low):
        if (len(temp_high) != 1) and ((len(temp_low) != 1)):
            raise IndexError("Arguments 'temp_low' and 'temp_high' "
                             "have to be of same length or one has "
                             "to be of length 1 !")

    # if factor_icing is not None and consider_icing is False:
    #     raise ValueError('Argument factor_icing can not be used without '
    #                      'setting consider_icing=True!')
    #
    # if factor_icing is None and consider_icing is True:
    #     raise ValueError('Icing cannot be considered because argument '
    #                      'factor_icing has value None!')

    # Make temp_low and temp_high have the same length and
    # convert unit to Kelvin.
    length = max([len(temp_high), len(temp_low)])
    if len(temp_high) == 1:
        list_temp_high_K = [temp_high[0] + 273.15] * length
    elif len(temp_high) == length:
        list_temp_high_K = [t + 273.15 for t in temp_high]
    if len(temp_low) == 1:
        list_temp_low_K = [temp_low[0] + 273.15] * length
    elif len(temp_low) == length:
        list_temp_low_K = [t + 273.15 for t in temp_low]

    # Calculate COPs depending on selected mode (without icing).
    if factor_icing is None:
        if mode == "heat_pump":
            cops = [quality_grade * t_h / (t_h - t_l) for
                    t_h, t_l in zip(list_temp_high_K, list_temp_low_K)]
        elif mode == "chiller":
            cops = [quality_grade * t_l / (t_h - t_l) for
                    t_h, t_l in zip(list_temp_high_K, list_temp_low_K)]

    # Calculate COPs of a heat pump and lower COP when icing occurs.
    elif factor_icing is not None:
        if mode == "heat_pump":
            cops = []
            for t_h, t_l in zip(list_temp_high_K, list_temp_low_K):
                if t_l < temp_threshold_icing + 273.15:
                    f_icing = factor_icing
                    cops = cops + [f_icing * quality_grade * t_h / (t_h - t_l)]
                if t_l >= temp_threshold_icing + 273.15:
                    cops = cops + [quality_grade * t_h / (t_h - t_l)]
        elif mode == "chiller":
            raise ValueError("Argument 'factor_icing' has "
                             "to be None for mode='chiller'!")
    return cops


def calc_max_Q_dot_chill(nominal_conditions, cops):
    r"""
    Calculates the maximal cooling capacity (relative value) of a chiller.

    Note
    ----
    This function assumes the cooling capacity of a chiller can exceed the
    rated nominal capacity (e.g., from the technical specification sheet).
    That means: The value of :py:obj:`max_Q_chill` can be greater than 1.
    Make sure your actual chiller is capable of doing so.
    If not, use 1 for the maximal cooling capacity.

    .. calc_max_Q_dot_chill-equations:

        :math:`\dot{Q}_\mathrm{chilled, max}
        = \frac{COP_\mathrm{actual}}{COP_\mathrm{nominal}}`

    Parameters
    ----------
    nominal_conditions : dict
        Dictionary describing one operating point (e.g., operation under STC)
        of the chiller by its
        cooling capacity, its electricity consumption and its COP
        ('nominal_Q_chill', 'nominal_el_consumption' and 'nominal_cop')
    cops : list of numerical values
        Actual COP

    Returns
    -------
    max_Q_chill : list of numerical values
        Maximal cooling capacity (relative value). Value is equal or greater
        than 0 and can be greater than 1.


    """
    if not isinstance(cops, list):
        raise TypeError("Argument 'cops' is not of type list!")

    nominal_cop = (nominal_conditions['nominal_Q_chill'] / nominal_conditions[
        'nominal_el_consumption'])
    max_Q_chill = [actual_cop / nominal_cop for actual_cop in cops]
    return max_Q_chill


def calc_max_Q_dot_heat(nominal_conditions, cops):
    r"""
        Calculates the maximal heating capacity (relative value) of a
        heat pump.

        Note
        ----
        This function assumes the heating capacity of a heat pump can exceed
        the rated nominal capacity (e.g., from the technical specification
        sheet). That means: The value of :py:obj:`max_Q_hot` can be greater
        than 1.
        Make sure your actual heat pump is capable of doing so.
        If not, use 1 for the maximal heating capacity.

    .. calc_max_Q_dot_heat-equations:

        :math:`\dot{Q}_\mathrm{hot, max}
        = \frac{COP_\mathrm{actual}}{COP_\mathrm{nominal}}`

        Parameters
        ----------
        nominal_conditions : dict
            Dictionary describing one operating point (e.g., operation
            under STC) of the heat pump by its
            heating capacity, its electricity consumption and its COP
            ('nominal_Q_hot', 'nominal_el_consumption' and 'nominal_cop')
        cops : list of numerical values
            Actual COP

        Returns
        -------
        max_Q_hot : list of numerical values
            Maximal heating capacity (relative value). Value is equal or
            greater than 0 and can be greater than 1.

        """
    nominal_cop = (nominal_conditions['nominal_Q_hot'] / nominal_conditions[
        'nominal_el_consumption'])
    max_Q_hot = [actual_cop / nominal_cop for actual_cop in cops]
    return max_Q_hot


def calc_chiller_quality_grade(nominal_conditions):
    r"""
    Calculates the quality grade for a given point of operation.

    Note
    ----
    This function is rather experimental.
    Please do not use it to estimate the quality grade of a real machine.
    A single point of operation might not be representative!

    .. calc_chiller_quality_grade-equations:

        :math:`\eta =
        \frac{\dot{Q}_\mathrm{chilled,nominal}}{P_\mathrm{el}} /
        \frac{T_\mathrm{low, nominal}}{T_\mathrm{high, nominal}
        - T_\mathrm{low, nominal}}`

    Parameters
    ----------
    nominal_conditions : dict
        Dictionary describing one operating point (e.g., operation under STC)
        of the chiller by its
        cooling capacity, its electricity consumption and its COP
        ('nominal_Q_chill', 'nominal_el_consumption' and 'nominal_cop')

    Returns
    -------
    q_grade : numerical value
        Quality grade

    """
    t_h = nominal_conditions['t_high_nominal'] + 273.15
    t_l = nominal_conditions['t_low_nominal'] + 273.15
    nominal_cop = (nominal_conditions['nominal_Q_chill'] / nominal_conditions[
        'nominal_el_consumption'])
    q_grade = nominal_cop / (t_l / (t_h - t_l))
    return q_grade
