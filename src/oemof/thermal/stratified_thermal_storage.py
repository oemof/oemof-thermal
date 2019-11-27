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
        Thickness of isolation layer [mm]

    lamb_iso : numeric
        Thermal conductivity of isolation layer [W/(m*K)]

    alpha_inside : numeric
        Heat transfer coefficient at the inner surface of the storage [W/(m2*K)]

    alpha_outside : numeric
        Heat transfer coefficient at the outer surface of the storage [W/(m2*K)]

    Returns
    ------
    u_value : numeric
        Thermal transmittance (U-value) [W/(m2*K)]
    """
    denominator = 1 / alpha_inside + s_iso * 1e-3 / lamb_iso + 1 / alpha_outside
    u_value = 1 / denominator

    return u_value


def calculate_storage_dimensions(height, diameter):
    r"""
    Calculates volume and total surface of a hot water storage.

    .. calculate_storage_dimensions-equations:

    :math:`V = \pi \frac{d^2}{4} \cdot h`

    :math:`A = \pi d h + 2 \pi \frac{d^2}{4}`

    Parameters
    ----------
    height : numeric
        Height of the storage [m]

    diameter : numeric
        Diameter of the storage [m]

    Returns
    -------
    volume : numeric
        Volume of storage

    surface : numeric
        Total surface of storage [m2]
    """
    volume = diameter**2 * 1 / 4 * np.pi * height
    surface = np.pi * diameter * height + 2 * np.pi * diameter**2 * 1 / 4

    return volume, surface


def calculate_capacities(volume, temp_h, temp_c, nonusable_storage_volume,
                         heat_capacity=4180, density=971.78):
    r"""
    Calculates the nominal storage capacity, surface area, minimum
    and maximum storage level of a stratified thermal storage.

    .. calculate_capacities-equations:

    :math:`Q_N = \pi \frac{d^2}{4} \cdot h \cdot c \cdot \rho \cdot \left( T_{H} - T_{C} \right)`

    :math:`Q_{max} = Q_N \cdot (1-v_{nonusable}/2)`

    :math:`Q_{min} = Q_N \cdot v_{nonusable}/2`

    Parameters
    ----------
    volume :numeric
        Volume of the storage[m]

    temp_h : numeric
        Temperature of hot storage medium [deg C]

    temp_c : numeric
        Temperature of cold storage medium [deg C]

    nonusable_storage_volume : numeric
        Share of storage volume that is not usable due to occupation by
        storage inlets [-].

    heat_capacity: numeric
        Average specific heat capacity of storage medium [J/(kg*K)]

    density : numeric
        Average density of storage medium [kg/m3]

    Returns
    -------
    nominal_storage_capacity : numeric
        Maximum amount of stored thermal energy [MWh]

    max_storage_level : numeric
        Maximal storage content relative to nominal storage capacity [-]

    min_storage_level : numeric
        Minimal storage content relative to nominal storage capacity [-]

    """
    nominal_storage_capacity = 1e-6 / 3600 * volume * heat_capacity * density * (temp_h - temp_c)
    max_storage_level = (1 - nonusable_storage_volume / 2)
    min_storage_level = nonusable_storage_volume / 2

    return nominal_storage_capacity, max_storage_level, min_storage_level


def calculate_losses(u_value, diameter, temp_h, temp_c, temp_env,
                     time_increment=1, heat_capacity=4180, density=971.78):
    r"""
    Calculates loss rate and fixed losses for a stratified thermal storage.

    .. calculate_losses-equations:

    :math:`\beta = U \frac{4}{D\rho c}\Delta t`

    :math:`\gamma = U \frac{4}{D\rho c \Delta T_{HC}}\Delta T_{C0}\Delta t`

    :math:`\delta = U \frac{\pi D^2}{4}\Big(\Delta T_{H0} + \Delta T_{C0}\Big)`

    Parameters
    ----------
    u_value : numeric
        Thermal transmittance of storage envelope [W/(m2*K)]

    diameter

    temp_h : numeric
        Temperature of hot storage medium [deg C]

    temp_c : numeric
        Temperature of cold storage medium [deg C]

    temp_env : numeric
        Temperature outside of the storage [deg C]

    time_increment : numeric
        Time increment of the :class:`oemof.solph.EnergySystem` [h]

    heat_capacity: numeric
        Average specific heat capacity of storage medium [J/(kg*K)]

    density : numeric
        Average density of storage medium [kg/m3]

    Returns
    -------
    loss_rate : numeric
        Loss rate of storage content [-]

    fixed_losses : numeric
        Fixed losses related to nominal storage capacity
        independent of storage content [-]

    fixed_absolute_losses : numeric
        Fixed losses independent of storage content
        and nominal storage capacity [MWh]
    """
    loss_rate = 4 * u_value * (temp_h - temp_c) * 1 / (diameter * density * heat_capacity) * time_increment
    fixed_losses = 4 * u_value * 1 / (diameter * density * heat_capacity) * (temp_c - temp_env) * time_increment
    fixed_absolute_losses = np.pi * diameter**2 * 0.25 * (temp_h + temp_c - 2 * temp_env) * time_increment

    return loss_rate, fixed_losses, fixed_absolute_losses
