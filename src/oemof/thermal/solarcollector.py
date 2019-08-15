"""Defines all functions, which are necessary for a thermal solar collector.
The solph-component-facade will be in another file"""

import pvlib
import pandas as pd


def solarcollector_precalc(df, periods,
                           lat, long, tz,
                           col_tilt, col_azimuth,
                           eta_0, c_1, c_2,
                           col_inlet_temp, delta_t_n,
                           date_col='date', irradiance_global_col='ghi',
                           irradiance_diffuse_col='dhi',  t_amb_col='t_amb'):
    """
    Calculates collectors efficiency and irradiance

    Parameters
    ---------
    df: dataframe
        holding values for time, the global and diffuse horizontal irradiance
        and the ambient temp.
    periods: numeric
        defines the number of timesteps
    lat, long: numeric
        latitude and longitude of the location
    tz: string
        pytz timezone of the location
    col_tilt, col_azimuth: numeric
        the tilt and azimuth of the collector. Azimuth according to pvlib
        in decimal degrees East of North
    eta_0: numeric
        optical efficiency of the collector
    c_1, c_2: numeric
        thermal loss parameters
    col_inlet_temp: numeric or series with length periods
        collectors inlet temperature
    delta_t_n:
        temperature difference between collector inlet and mean temperature
    date_col, irradiance_global_col, irradiance_diffuse_col, t_amb_col: string
        describes the name of the columns in the dataframe df
        defaults: 'date', 'ghi', 'dhi', 't_amb'

    Returns
    -------
    DataFrame
        The DataFrame will have the following columns:
        col_ira
        eta_c
    right now, the dataframe have more columns to test the function. will be
    removed later

    col_ira: the irradiance on tilted collector
    eta_c: efficiency of the collector

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
