# -*- coding: utf-8

"""
This module is designed to hold functions which are necessary for the CSP.

This file is part of project oemof (github.com/oemof/oemof-thermal). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location:
oemof-thermal/src/oemof/thermal/concentrating_solar_power.py

SPDX-License-Identifier: MIT
"""


import pvlib
import pandas as pd
import numpy as np
import warnings


def csp_precalc(lat, long, collector_tilt, collector_azimuth, cleanliness,
                eta_0, c_1, c_2,
                temp_collector_inlet, temp_collector_outlet, temp_amb,
                a_1, a_2, a_3=0, a_4=0, a_5=0, a_6=0,
                loss_method='Janotte',
                irradiance_method='horizontal',
                **kwargs):
    r"""
    Calculates collectors efficiency and irradiance according to [1] and the
    heat of the thermal collector. For the calculation of irradiance pvlib [2]
    is used.

    .. csp_precalc_equation:

    :math:`Q_{coll} = E_{coll} \cdot \eta_C`

    functions used
     * pvlib.solarposition.get_solarposition
     * pvlib.tracking.singleaxis
     * calc_irradiance
     * calc_collector_irradiance
     * calc_iam
     * calc_eta_c
     * calc_heat_coll

    Parameters
    ----------
    lat: numeric
        Latitude of the location.

    long: numeric
        Longitude of the location.

    collector_tilt: numeric
        The tilt of the collector.

    collector_azimuth: numeric
        The azimuth of the collector. Azimuth according to pvlib in decimal
        degrees East of North.

    cleanliness: numeric
        Cleanliness of the collector (between 0 and 1).

    a_1, a_2, a_3, a_4, a_5, a_6: numeric
        Parameters for the incident angle modifier. For loss method 'Janotte'
        a_1 and a_2 are required, for 'Andasol' a_1 to a_6 are required.

    eta_0: numeric
        Optical efficiency of the collector.

    c_1: numeric
        Thermal loss parameter 1. Required for both loss methods.

    c_2: numeric
        Thermal loss parameter 2. Required for loss method 'Janotte'. If loss
        method 'Andasol' is used, set it to 0.

    temp_collector_inlet: numeric or series with length periods
        Collectors inlet temperature.

    temp_collector_outlet: numeric or series with length periods
        Collectors outlet temperature.

    temp_amb: time indexed series
        Ambient temperature time series.

    loss_method: string, default 'Janotte'
        Valid values are: 'Janotte' or 'Andasol'. Describes, how the thermal
        losses and the incidence angle modifier are calculated.

    irradiance_method: string, default 'horizontal'
        Valid values are: 'horizontal' or 'normal'. Describes, if the
        horizontal direct irradiance or the direct normal irradiance is
        given and used for calculation.

    E_dir_hor/dni (depending on irradiance_method): time indexed series
        Irradiance for calculation.

    Returns
    -------
    data : pandas.DataFrame
        Dataframe containing the following columns

        * collector_irradiance
        * eta_c
        * collector_heat

        collector_irradiance is the irradiance which reaches the collector after all
        losses (incl. cleanliness).


    **Comment**

    Series for ambient temperature and irradiance must have the same length
    and the same time index. Be aware of the time one.

    **Proposal of values**

    If you have no idea, which values your collector have, here are values,
    which were measured in [1] for a collector:
    a1: -0.00159, a2: 0.0000977,
    eta_0: 0.816, c1: 0.0622, c2: 0.00023.

    **Reference**

    [1] Janotte, N; et al: Dynamic performance evaluation of the HelioTrough \
    collector demon-stration loop - towards a new benchmark in parabolic \
    trough qualification, SolarPACES 2013

    [2] William F. Holmgren, Clifford W. Hansen, and Mark A. Mikofski.
    “pvlib python: a python package for modeling solar energy systems.”
    Journal of Open Source Software, 3(29), 884, (2018).
    https://doi.org/10.21105/joss.00884
    """

    if loss_method not in ['Janotte', 'Andasol']:
        raise ValueError(
            "loss_method should be 'Janotte' or 'Andasol'")

    if irradiance_method not in ['normal', 'horizontal']:
        raise ValueError(
            "irradiance_method should be 'normal' or 'horizontal'")

    required_dict = {'horizontal': 'E_dir_hor', 'normal': 'dni'}

    irradiance_required = required_dict[irradiance_method]

    if irradiance_required not in kwargs:
        raise AttributeError(
            f"'{irradiance_required}' necessary for {irradiance_method} is not provided")

    if loss_method == 'Andasol' and (c_2 != 0):
        warnings.warn(
            "Parameter c_2 is not used for loss method 'Andasol'")

    if loss_method == 'Andasol' and (a_3 == 0 or a_4 == 0 or a_5 == 0 or a_6 == 0):
        warnings.warn(
            "Parameters a_3 to a_6 are required for loss method 'Andasol'")

    irradiance = kwargs.get(irradiance_required)

    if not temp_amb.index.equals(irradiance.index):
        raise IndexError(f"Index of temp_amb and {irradiance_required} have to be the same.")

    # Creation of a df with 2 columns
    data = pd.DataFrame({'irradiance': irradiance,
                         't_amb': temp_amb})

    # Calculation of geometrical position of collector with the pvlib
    solarposition = pvlib.solarposition.get_solarposition(
        time=data.index,
        latitude=lat,
        longitude=long)

    # Calculation of the tracking data with the pvlib
    tracking_data = pvlib.tracking.singleaxis(
        solarposition['apparent_zenith'], solarposition['azimuth'],
        axis_tilt=collector_tilt, axis_azimuth=collector_azimuth)

    # Calculation of the irradiance which hits the collectors surface
    irradiance_on_collector = calc_irradiance(
        tracking_data['surface_tilt'], tracking_data['surface_azimuth'],
        solarposition['apparent_zenith'], solarposition['azimuth'],
        data['irradiance'], irradiance_method)

    # Calculation of the irradiance which reaches the collector after all
    # losses (cleanliness)
    collector_irradiance = calc_collector_irradiance(
        irradiance_on_collector, cleanliness)

    # Calculation of the incidence angle modifier
    iam = calc_iam(
        a_1, a_2, a_3, a_4, a_5, a_6, tracking_data['aoi'], loss_method)

    # Calculation of the collectors efficiency
    eta_c = calc_eta_c(
        eta_0, c_1, c_2, iam, temp_collector_inlet, temp_collector_outlet,
        data['t_amb'], collector_irradiance, loss_method)

    # Calculation of the collectors heat
    collector_heat = calc_heat_coll(
        eta_c, collector_irradiance)

    # Writing the results in the output df
    data['collector_irradiance'] = collector_irradiance
    data['eta_c'] = eta_c
    data['collector_heat'] = collector_heat

    return data


def calc_irradiance(surface_tilt, surface_azimuth, apparent_zenith, azimuth,
                    irradiance, irradiance_method):
    r"""

    Parameters
    ----------
    surface_tilt: series of numeric
        Panel tilt from horizontal.

    surface_azimuth: series of numeric
        Panel azimuth from north.

    apparent_zenith: series of numeric
        Solar zenith angle.

    azimuth: series of numeric
        Solar azimuth angle.

    irradiance: series of numeric
        Solar irraciance (dni or E_direct_horizontal).

    irradiance_method: str
        Describes, if the horizontal direct irradiance or the direct normal
        irradiance is given and used for calculation.

    Returns
    -------
    irradiance_on_collector: series of numeric
        Irradiance which hits collectors surface.

    """
    if irradiance_method == 'horizontal':
        poa_horizontal_ratio = pvlib.irradiance.poa_horizontal_ratio(
            surface_tilt, surface_azimuth, apparent_zenith, azimuth)
        poa_horizontal_ratio[poa_horizontal_ratio < 0] = 0
        irradiance_on_collector = irradiance * poa_horizontal_ratio

    elif irradiance_method == 'normal':
        irradiance_on_collector = pvlib.irradiance.beam_component(
            surface_tilt, surface_azimuth, apparent_zenith, azimuth,
            irradiance)

    return irradiance_on_collector


def calc_collector_irradiance(irradiance_on_collector, cleanliness):
    r"""
    Subtracts the losses of dirtiness from the irradiance on the collector

    .. calc_collector_irradiance_equation:

    :math:`E_{coll} = E^*_{coll} \cdot X^{3/2}`

    Parameters
    ----------
    irradiance_on_collector: series of numeric
        Irradiance which hits collectors surface.

    x: numeric
        Cleanliness of the collector (between 0 and 1).

    Returns
    -------
    collector_irradiance: series of numeric
        Irradiance on collector after all losses.
    """
    collector_irradiance = irradiance_on_collector * cleanliness**1.5
    collector_irradiance[collector_irradiance < 0] = 0
    collector_irradiance = collector_irradiance.fillna(0)

    return collector_irradiance


def calc_iam(a_1, a_2, a_3, a_4, a_5, a_6, aoi, loss_method):
    r"""
    Calculates the incidence angle modifier depending on the loss method

    .. calc_iam_equation:

    method 'Janotte':

    :math:`\kappa(\varTheta) = 1 - a_1 \cdot \vert\varTheta\vert- a_2
    \cdot \vert\varTheta\vert^2`

    method 'Andasol':

    :math:`\kappa(\varTheta) = 1 - a_1 \cdot \vert\varTheta\vert - a_2
    \cdot \vert\varTheta\vert^2- a_3 \cdot \vert\varTheta\vert^3
    - a_4 \cdot \vert\varTheta\vert^4 - a_5 \cdot \vert\varTheta\vert^5
    - a_6 \cdot \vert\varTheta\vert^6`

    Parameters
    ----------
    a_1, a_2, a_3, a_4, a_5, a_6: numeric
        Parameters for the incident angle modifier. For loss method 'Janotte'
        a_1 and a_2 are required, for 'Andasol' a_1 to a_6 are required.

    aoi: series of numeric
        Angle of incidence.

    loss_method: string, default 'Janotte'
        Valid values are: 'Janotte' or 'Andasol'. Describes, how the thermal
        losses and the incidence angle modifier are calculated.

    Returns
    -------
    Incidence angle modifier: series of numeric

    """
    if loss_method == 'Janotte':
        iam = 1 - a_1 * abs(aoi) - a_2 * aoi**2

    if loss_method == 'Andasol':
        iam = (1 - a_1 * abs(aoi) - a_2 * aoi**2 - a_3 * aoi**3 - a_4 * aoi**4
               - a_5 * aoi**5 - a_6 * aoi**6)
    return iam


def calc_eta_c(eta_0, c_1, c_2, iam,
               temp_collector_inlet, temp_collector_outlet, temp_amb,
               collector_irradiance, loss_method):
    r"""
    Calculates collectors efficiency depending on the loss method

    .. calc_eta_c_equation:

    method 'Janotte':

    :math:`\eta_C = \eta_0 \cdot \kappa(\varTheta) - c_1 \cdot
    \frac{\Delta T}{E_{coll}} - c_2 \cdot \frac{{\Delta T}^2}{E_{coll}}`

    method 'Andasol':

    :math:`\eta_C = \eta_0 \cdot \kappa(\varTheta) - \frac{c_1}{E_{coll}}`

    Parameters
    ----------
    eta_0: numeric
        Optical efficiency of the collector.

    c_1: numeric
        Thermal loss parameter 1. Required for both loss methods.

    c_2: numeric
        Thermal loss parameter 2. Required for loss method 'Janotte'.

    iam: series of numeric
        Incidence angle modifier.

    temp_collector_inlet: numeric, in °C
        Collectors inlet temperature.

    temp_collector_outlet: numeric, in °C
        Collectors outlet temperature.

    temp_amb: series of numeric, in °C
        Ambient temperature.

    collector_irradiance: series of numeric
        Irradiance on collector after all losses.

    loss_method: string, default 'Janotte'
        Valid values are: 'Janotte' or 'Andasol'. Describes, how the thermal
        losses and the incidence angle modifier are calculated.

    Returns
    -------
    collectors efficiency: series of numeric

    """

    if loss_method == 'Janotte':
        delta_temp = (temp_collector_inlet + temp_collector_outlet) / 2 - temp_amb
        eta_c = eta_0 * iam - c_1 * delta_temp / collector_irradiance - c_2\
            * delta_temp ** 2 / collector_irradiance

    if loss_method == 'Andasol':
        eta_c = eta_0 * iam - c_1 / collector_irradiance

    eta_c[eta_c < 0] = 0
    eta_c[eta_c == np.inf] = 0
    eta_c = eta_c.fillna(0)
    return eta_c


def calc_heat_coll(eta_c, collector_irradiance):
    r"""
    .. csp_heat_equation:

    :math:`\dot Q_{coll} = E_{coll} \cdot \eta_C`

    Parameters
    ----------
    eta_c: series of numeric
        collectors efficiency.

    collector_irradiance: series of numeric
        Irradiance on collector after all losses.

    Returns
    -------
    collectors heat: series of numeric

    """
    collector_heat = collector_irradiance * eta_c
    return collector_heat
