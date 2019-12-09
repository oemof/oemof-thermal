# -*- coding: utf-8 -

"""
This module is designed to hold functions for calculating a solar thermal collector.

This file is part of project oemof (github.com/oemof/oemof-thermal). It's copyrighted by the contributors recorded in the version control history of the file, available from its original location:
oemof-thermal/src/oemof/thermal/flat_plate_collector.py
"""

import pvlib
import pandas as pd


def flat_plate_precalc(df, periods,
                           lat, long, tz,
                           col_tilt, col_azimuth,
                           eta_0, c_1, c_2,
                           col_inlet_temp, delta_t_n,
                           date_col='date',
                           irradiance_global_col='ghi',
                           irradiance_diffuse_col='dhi',
                           t_amb_col='t_amb'):
    """
    Calculates collectors efficiency and irradiance of a flat plate collector.

    ..calculate_collectors efficiency:

    :math:``

    Parameters
    ---------
    df: dataframe
        Holds values for time, the global and diffuse horizontal irradiance and the ambient temp (in Celsius degrees).
    periods: numeric
        Defines the number of timesteps.
    lat, long: numeric
        Latitude and longitude of the location.
    tz: string
        pytz timezone of the location.
    col_tilt, col_azimuth: numeric
        Tilt and azimuth of the collector. Azimuth according to pvlib
        in decimal degrees East of North.
    eta_0: numeric
        Optical efficiency of the collector.
    c_1, c_2: numeric
        Thermal loss parameters.
    col_inlet_temp: numeric or series with length of periods
        Collectors inlet temperature.
    delta_t_n:
        Temperature difference between collector inlet and mean temperature.
    date_col, irradiance_global_col, irradiance_diffuse_col, t_amb_col: string
        Describes the name of the columns in the dataframe df.
        Defaults: 'date', 'ghi', 'dhi', 't_amb'

    Returns
    -------
    DataFrame
        The DataFrame will have the following columns:
        col_ira
        eta_c
        collector_heat

    col_ira:
        The irradiance on the tilted collector.
    eta_c:
        The efficiency of the collector.
    collector_heat:
        The heat power output of the collector.

    """

    date_time_index = pd.date_range(df.loc[0, date_col], periods=periods,
                                    freq='H', tz=tz)
    datainput = df.iloc[:periods]

    data = pd.DataFrame({'date': date_time_index,
                         'ghi': datainput[irradiance_global_col],
                         'dhi': datainput[irradiance_diffuse_col],
                         't_amb': datainput[t_amb_col]})

    data.set_index('date', inplace=True)

    solposition = pvlib.solarposition.get_solarposition(
        time=date_time_index,
        latitude=lat,
        longitude=long)

    dni = pvlib.irradiance.dni(ghi=data['ghi'],
                               dhi=data['dhi'],
                               zenith=solposition['apparent_zenith'])

    total_irradiation = pvlib.irradiance.get_total_irradiance(
        surface_tilt=col_tilt,
        surface_azimuth=col_azimuth,
        solar_zenith=solposition['apparent_zenith'],
        solar_azimuth=solposition['azimuth'],
        dni=dni.fillna(0),  # fill NaN values with '0'
        ghi=data['ghi'],
        dhi=data['dhi'])

    data['col_ira'] = total_irradiation['poa_global']

    eta_c = calc_eta_c(eta_0, c_1, c_2, col_inlet_temp, delta_t_n,
                       data['t_amb'], total_irradiation['poa_global'])
    data['eta_c'] = eta_c
    collectors_heat = eta_c * total_irradiation['poa_global']
    data["collectors_heat"] = collectors_heat

    return data


def calc_eta_c(eta_0, c_1, c_2, col_inlet_temp, delta_t_n, t_amb, col_ira):
    delta_t = col_inlet_temp + delta_t_n - t_amb
    eta_c = pd.Series()
    for index, value in col_ira.items():
        if value > 0:
            eta = eta_0 - c_1 * delta_t[index] / value - c_2 * delta_t[
                index] ** 2 / value
            if eta > 0:
                eta_c[index] = eta
            else:
                eta_c[index] = 0
        else:
            eta_c[index] = 0
    return eta_c
