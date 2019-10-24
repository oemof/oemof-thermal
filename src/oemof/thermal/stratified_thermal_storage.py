# -*- coding: utf-8 -

"""
This module is designed to hold functions for calculating stratified thermal storages.

This file is part of project oemof (github.com/oemof/oemof-thermal). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location:
oemof-thermal/src/oemof/thermal/stratified_thermal_storage.py
"""

import numpy as np


def calculate_storage_u_value(s_iso, lamb_iso, alpha_inside, alpha_outside):
    r"""
    Calculates the thermal transmittance (U-value) of a thermal storage.

    .. calculate_storage_u_value-equations:

    :math:`U = \frac{1}{\frac{1}{\alpha_i} + \frac{s_{iso}}{\lambda_ {iso}} + \frac{1}{\alpha_a}}`

    Parameters
    ----------
    s_iso : numeric
    lamb_iso : numeric
    alpha_inside : numeric
    alpha_outside : numeric

    Returns
    ------
    u_value : numeric
    """
    denominator = 1 / alpha_inside + s_iso / lamb_iso + 1 / alpha_outside
    u_value = 1 / denominator

    return u_value


def calculate_capacities(height, diameter, temp_h, temp_c, nonusable_storage_volume,
                         heat_capacity=4180, density=971.78):
    r"""
    Calculates the nominal storage capacity, surface area, minimum
    and maximum storage level of a stratified thermal storage.

    .. calculate_capacities-equations:

    :math:`Q_{max} = Q_N \cdot (1-\beta/2)`

    :math:`Q_{min} = Q_N \cdot \beta/2`

    :math:`Q_N = \frac{d^2}{4} \cdot \pi \cdot h \cdot c \cdot \rho \cdot \left( T_{H} - T_{C} \right)`

    Parameters
    ----------
    height : numeric
    diameter : numeric
    temp_h : numeric
    temp_c : numeric
    nonusable_storage_volume : numeric
    heat_capacity: numeric
    density : numeric

    Returns
    -------
    nominal_storage_capacity : numeric
    surface : numeric
    max_storage_level : numeric
    min_storage_level : numeric
    """
    nominal_storage_capacity = 1/3600 * diameter**2 * 1/4 * np.pi * height * heat_capacity * density * (temp_h - temp_c)
    max_storage_level = (1 - nonusable_storage_volume/2)
    min_storage_level = nonusable_storage_volume/2
    surface = np.pi * diameter * height + 2 * np.pi * diameter**2 * 1/4

    return nominal_storage_capacity, surface, max_storage_level, min_storage_level


def calculate_losses(nominal_storage_capacity, u_value, surface, temp_h, temp_c, temp_env):
    r"""
    Calculates loss rate and fixed losses for a stratified thermal storage.

    .. calculate_losses-equations:

    \beta =  U \cdot A \cdot \DeltaT_{HC} / Q_N
    \gamma = U \cdot A \cdot \DeltaT_{C0} / Q_N

    Parameters
    ----------
    nominal_storage_capacity : numeric
    u_value : numeric
    surface : numeric
    temp_h : numeric
    temp_c : numeric
    temp_env : numeric

    Returns
    -------
    loss_rate : numeric
    fixed_losses : numeric
    """
    loss_rate =    u_value * surface * (temp_h - temp_c)   * 1 / nominal_storage_capacity
    fixed_losses = u_value * surface * (temp_c - temp_env) * 1 / nominal_storage_capacity

    return loss_rate, fixed_losses
