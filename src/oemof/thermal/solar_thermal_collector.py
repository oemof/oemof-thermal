# -*- coding: utf-8

"""
This module is designed to hold functions for calculating a solar thermal collector.

This file is part of project oemof (github.com/oemof/oemof-thermal). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location:
oemof-thermal/src/oemof/thermal/solar_thermal_collector.py

SPDX-License-Identifier: MIT
"""


import pvlib
import pandas as pd


def flat_plate_precalc(
    lat,
    long,
    collector_tilt,
    collector_azimuth,
    eta_0,
    a_1,
    a_2,
    temp_collector_inlet,
    delta_temp_n,
    irradiance_global,
    irradiance_diffuse,
    temp_amb
):
    r"""
    Calculates collectors heat, efficiency and irradiance
    of a flat plate collector.

    .. flat_plate_precalc_equation:

    :math:`\dot Q_{coll} = E_{coll} \cdot \eta_C`

    Parameters
    ----------
    lat: numeric
        Latitude of the location.

    long: numeric
        Longitude of the location.

    collector_tilt: numeric
        The tilt of the collector.

    collector_azimuth: numeric
        The azimuth of the collector. Azimuth according to pvlib in decimal degrees East of North.

    eta_0: numeric
        Optical efficiency of the collector.

    a_1, a_2: numeric
        Thermal loss parameters.

    temp_collector_inlet: numeric or series with length of periods
        Collectors inlet temperature.

    delta_temp_n: numeric
        Temperature difference between collector inlet and mean temperature.

    irradiance_global: time indexed series
        Global horizontal irradiance.

    irradiance_diffuse: time indexed series
        Diffuse irradiance.

    temp_amb: time indexed series
        Ambient temperature.

    Returns
    -------
    data : pandas.DataFrame
        DataFrame containing the followiing columns:

        * col_ira: The irradiance on the tilted collector.
        * eta_c: The efficiency of the collector.
        * collector_heat: The heat power output of the collector.
    """

    # Creation of a df with 3 columns
    data = pd.DataFrame(
        {
            'ghi': irradiance_global,
            'dhi': irradiance_diffuse,
            'temp_amb': temp_amb
        }
    )

    # date_time_index = pd.date_range(
    #     df.loc[0, date_col], periods=periods, freq='H', tz=tz
    # )
    # datainput = df.iloc[:periods]

    # data.set_index('date', inplace=True)

    # Calculation of geometrical position of collector with the pvlib
    solposition = pvlib.solarposition.get_solarposition(
        time=data.index, latitude=lat, longitude=long
    )

    dni = pvlib.irradiance.dni(
        ghi=data['ghi'], dhi=data['dhi'], zenith=solposition['apparent_zenith']
    )

    total_irradiation = pvlib.irradiance.get_total_irradiance(
        surface_tilt=collector_tilt,
        surface_azimuth=collector_azimuth,
        solar_zenith=solposition['apparent_zenith'],
        solar_azimuth=solposition['azimuth'],
        dni=dni.fillna(0),  # fill NaN values with '0'
        ghi=data['ghi'],
        dhi=data['dhi'],
    )

    data['col_ira'] = total_irradiation['poa_global']

    eta_c = calc_eta_c_flate_plate(
        eta_0,
        a_1,
        a_2,
        temp_collector_inlet,
        delta_temp_n,
        data['temp_amb'],
        total_irradiation['poa_global'],
    )
    data['eta_c'] = eta_c
    collectors_heat = eta_c * total_irradiation['poa_global']
    data["collectors_heat"] = collectors_heat

    return data


def calc_eta_c_flate_plate(
    eta_0,
    a_1,
    a_2,
    temp_collector_inlet,
    delta_temp_n,
    temp_amb,
    collector_irradiance,
):
    r"""
    Calculates collectors efficiency

    .. calc_eta_c_flate_plate_equation:

    :math:`\eta_C = \eta_0 - a_1 \cdot \frac{\Delta T}{E_{coll}}
    - a_2 \cdot \frac{{\Delta T}^2}{E_{coll}}`

    with

    :math:`\Delta T = T_{coll,in} + {\Delta T}_n - T_{amb}`

    Parameters
    ----------
    eta_0: numeric
         Optical efficiency of the collector.
    a_1: numeric
        Thermal loss parameter 1.
    a_2: numeric
        Thermal loss parameter 2.
    temp_collector_inlet: numeric, in °C
        Collectors inlet temperature.
    delta_temp_n: numeric
        Temperature difference between collector inlet and mean temperature.
    temp_amb: series of numeric, in °C
        Ambient temperature.
    collector_irradiance: series of numeric
        Irradiance on collector after all losses.

    Returns
    -------
    eta_c: series of numeric
        collectors efficiency

    """
    delta_t = temp_collector_inlet + delta_temp_n - temp_amb
    eta_c = pd.Series()
    for index, value in collector_irradiance.items():
        if value > 0:
            eta = (
                eta_0
                - a_1 * delta_t[index] / value
                - a_2 * delta_t[index] ** 2 / value
            )
            if eta > 0:
                eta_c[index] = eta
            else:
                eta_c[index] = 0
        else:
            eta_c[index] = 0
    return eta_c
