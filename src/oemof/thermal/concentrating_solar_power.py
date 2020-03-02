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


def csp_precalc(df, periods,
                lat, long, timezone,
                collector_tilt, collector_azimuth, cleanliness,
                eta_0, c_1, c_2,
                temp_collector_inlet, temp_collector_outlet,
                a_1, a_2, a_3=0, a_4=0, a_5=0, a_6=0,
                loss_method='Janotte',
                irradiance_method='horizontal',
                date_col='date', irradiance_col='E_dir_hor',
                temp_amb_col='t_amb'):
    r"""
    Calculates collectors efficiency and irradiance according to [1] and the
    heat of the thermal collector. For the calculation of irradiance pvlib [2]
    is used.

    .. csp_precalc_equation:

    :math:`Q_{coll} = E_{coll} \cdot \eta_C`

    functions used
     * calc_collector_irradiance
     * calc_iam
     * calc_eta_c

    Parameters
    ----------
    df: dataframe
        Holds values for time, the irradiance and the ambient temperature.
    periods: numeric
        Defines the number of timesteps.
    lat: numeric
        Latitude of the location.
    long: numeric
        Longitude of the location.
    timezone: string
        pytz timezone of the location.
    collector_tilt: numeric
        The tilt of the collector.
    collector_azimuth: numeric
        The azimuth of the collector. Azimuth according to pvlib in decimal
        degrees East of North
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
        Thermal loss parameter 2. Required for loss method 'Janotte'.
    temp_collector_inlet: numeric or series with length periods
        Collectors inlet temperature.
    temp_collector_outlet: numeric or series with length periods
        Collectors outlet temperature.
    loss_method: string, default 'Janotte'
        Valid values are: 'Janotte' or 'Andasol'. Describes, how the thermal
        losses and the incidence angle modifier are calculated.
    irradiance_method: string, default 'horizontal'
        Valid values are: 'horizontal' or 'normal'. Describes, if the
        horizontal direct irradiance or the direct normal irradiance is
        given and used for calculation.
    date_col: string, default: 'date'
        Describes the name of the column in the dataframe df.
    irradiance_col: string, default: 'E_dir_hor'
        Describes the name of the column in the dataframe df.
    temp_amb_col: string, default: 'temp_amb'
        Describes the name of the column in the dataframe df.

    Returns
    -------
    DataFrame: with the following columns
        * collector_irradiance
        * eta_c
        * collector_heat

    collector_irradiance:
        The irradiance on collector after all losses which \
        occur before the light hits the collectors surface.


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
        raise ValueError("loss_method should be 'Janotte' or 'Andasol'")

    date_time_index = pd.date_range(df.loc[0, date_col], periods=periods,
                                    freq='H', tz=timezone)
    # Creation of input-DF with 3 columns, depending on irradiance_method
    datainput = df.iloc[:periods]

    if irradiance_method == 'horizontal':
        data = pd.DataFrame({'date': date_time_index,
                             'E_dir_hor': datainput[irradiance_col],
                             't_amb': datainput[temp_amb_col]})

    elif irradiance_method == 'normal':
        data = pd.DataFrame({'date': date_time_index,
                             'dni': datainput[irradiance_col],
                             't_amb': datainput[temp_amb_col]})
    else:
        raise AttributeError("irradiance_method must be 'horizontal' or"
                             "'normal'")

    data.set_index('date', inplace=True)

    # Calculation of geometrical position of collector with the pvlib
    solarposition = pvlib.solarposition.get_solarposition(
        time=date_time_index,
        latitude=lat,
        longitude=long)

    tracking_data = pvlib.tracking.singleaxis(
        solarposition['apparent_zenith'], solarposition['azimuth'],
        axis_tilt=collector_tilt, axis_azimuth=collector_azimuth)

    # Calculation of the irradiance which hits the collectors surface
    if irradiance_method == 'horizontal':
        poa_horizontal_ratio = pvlib.irradiance.poa_horizontal_ratio(
            tracking_data['surface_tilt'], tracking_data['surface_azimuth'],
            solarposition['apparent_zenith'], solarposition['azimuth'])
        poa_horizontal_ratio[poa_horizontal_ratio < 0] = 0

        irradiance_on_collector = data['E_dir_hor'] * poa_horizontal_ratio

    elif irradiance_method == 'normal':
        irradiance_on_collector = pvlib.irradiance.beam_component(
            tracking_data['surface_tilt'], tracking_data['surface_azimuth'],
            solarposition['apparent_zenith'], solarposition['azimuth'],
            data['dni'])

    # Calculation of the irradiance which reaches the collector after all
    # losses (cleanliness)
    collector_irradiance = calc_collector_irradiance(
        irradiance_on_collector, cleanliness)
    collector_irradiance = collector_irradiance.fillna(0)
    data['collector_irradiance'] = collector_irradiance

    # Calculation of the incidence angle modifier
    iam = calc_iam(a_1, a_2, a_3, a_4, a_5, a_6, tracking_data['aoi'],
                   loss_method)

    # Calculation of the collectors efficiency
    eta_c = calc_eta_c(eta_0, c_1, c_2, iam,
                       temp_collector_inlet, temp_collector_outlet,
                       data['t_amb'], collector_irradiance, loss_method)
    data['eta_c'] = eta_c

    # Calculation of the collectors heat
    collector_heat = calc_heat_coll(eta_c, collector_irradiance)
    data['collector_heat'] = collector_heat

    return data


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

    Parameters
    ----------
    eta_c: series of numeric
        collectors efficiency
    collector_irradiance: series of numeric
        Irradiance on collector after all losses.

    Returns
    -------
    collectors heat: series of numeric

    """
    collector_heat = collector_irradiance * eta_c
    return collector_heat
