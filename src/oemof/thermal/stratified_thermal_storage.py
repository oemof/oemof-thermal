# -*- coding: utf-8

"""
This module is designed to hold functions for calculating stratified thermal storages.

This file is part of project oemof (github.com/oemof/oemof-thermal). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location:
oemof-thermal/src/oemof/thermal/stratified_thermal_storage.py

SPDX-License-Identifier: MIT
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
    -------
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

    :math:`A = \pi d h + \pi \frac{d^2}{2}`

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
    volume = 0.25 * np.pi * diameter ** 2 * height
    surface = np.pi * diameter * height + 0.5 * np.pi * diameter ** 2

    return volume, surface


def calculate_capacities(
    volume, temp_h, temp_c, heat_capacity=4195.52, density=971.803
):
    r"""
    Calculates the nominal storage capacity, minimum
    and maximum storage level of a stratified thermal storage.

    .. calculate_capacities-equations:

    :math:`Q_N = V \cdot c \cdot \rho \cdot \left( T_{H} - T_{C} \right)`

    Parameters
    ----------
    volume :numeric
        Volume of the storage [m3]

    temp_h : numeric
        Temperature of hot storage medium [deg C]

    temp_c : numeric
        Temperature of cold storage medium [deg C]

    heat_capacity: numeric
        Average specific heat capacity of storage medium [J/(kg*K)]
        Default values calculated with CoolProp for a temperature of 80 °C
        as a simplifying assumption

    density : numeric
        Average density of storage medium [kg/m3]
        Default values calculated with CoolProp for a temperature of 80 °C
        as a simplifying assumption

    Returns
    -------
    nominal_storage_capacity : numeric
        Maximum amount of stored thermal energy [MWh]

    """
    nominal_storage_capacity = volume * heat_capacity * density * (temp_h - temp_c)
    nominal_storage_capacity *= 1 / 3600  # J to Wh
    nominal_storage_capacity *= 1e-6  # Wh to MWh

    return nominal_storage_capacity


def calculate_losses(
    u_value,
    diameter,
    temp_h,
    temp_c,
    temp_env,
    time_increment=1,
    heat_capacity=4195.52,
    density=971.803,
):
    r"""
    Calculates loss rate and fixed losses for a stratified thermal storage.

    .. calculate_losses-equations:

    :math:`\beta = U \frac{4}{d\rho c}\Delta t`

    :math:`\gamma = U \frac{4}{d\rho c \Delta T_{HC}}\Delta T_{C0}\Delta t`

    :math:`\delta = U \frac{\pi d^2}{4}\Big(\Delta T_{H0} + \Delta T_{C0}\Big)\Delta t`

    Parameters
    ----------
    u_value : numeric
        Thermal transmittance of storage envelope [W/(m2*K)]

    diameter : numeric
        Diameter of the storage [m]

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
        Default values calculated with CoolProp for a temperature of 80 °C
        as a simplifying assumption

    density : numeric
        Average density of storage medium [kg/m3]
        Default values calculated with CoolProp for a temperature of 80 °C
        as a simplifying assumption

    Returns
    -------

    loss_rate : numeric (sequence or scalar)
        The relative loss of the storage capacity between two consecutive
        timesteps [-]

    fixed_losses_relative : numeric (sequence or scalar)
        Losses independent of state of charge between two consecutive
        timesteps relative to nominal storage capacity [-]

    fixed_losses_absolute : numeric (sequence or scalar)
        Losses independent of state of charge and independent of
        nominal storage capacity between two consecutive timesteps [MWh]
    """
    loss_rate = (
        4 * u_value * 1 / (diameter * density * heat_capacity) * time_increment
        * 3600  # Ws to Wh
    )

    fixed_losses_relative = (
        4 * u_value * (temp_c - temp_env)
        * 1 / ((diameter * density * heat_capacity) * (temp_h - temp_c))
        * time_increment
        * 3600  # Ws to Wh
    )

    fixed_losses_absolute = (
        0.25 * u_value * np.pi * diameter ** 2 * (temp_h + temp_c - 2 * temp_env) * time_increment
    )

    fixed_losses_absolute *= 1e-6  # Wh to MWh

    return loss_rate, fixed_losses_relative, fixed_losses_absolute
