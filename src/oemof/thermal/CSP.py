"""Defines all functions, which are necessary for the CSP. The solph-component-
facade will be in another file"""

import pvlib
import pandas as pd

def csp_precalc(df, periods,
                lat, long, tz,
                col_tilt, col_azimuth, x, a1, a2,
                eta_0, c_1, c_2,
                col_inlet_temp, col_outlet_temp,
                irradiance='horizontal',
                date_col='date', irradiance_col='E_dir_hor',
                t_amb_col='t_amb'):
    """
    Calculates collectors efficiency and irradiance according to [1]

    Parameters
    ---------
    df: dataframe
        holding values for time, the irradiance and the ambient temp.
    periods: numeric
        defines the number of timesteps
    lat, long: numeric
        latitude and longitude of the location
    tz: string
        pytz timezone of the location
    col_tilt, col_azimuth: numeric
        the tilt and azimuth of the collector. Azimuth according to pvlib
        in decimal degrees East of North
    x: numeric
        Cleanliness of the collector (between 0 and 1)
    a1, a2: numeric
        parameters for the incident angle modifier
    eta_0: numeric
        optical efficiency of the collector
    c_1, c_2: numeric
        thermal loss parameters
    col_inlet_temp, col_outlet_temp: numeric or series with length periods
        collectors inlet and outlet temperatures
    irradiance: string, default 'horizontal'
        values: 'horizontal' or 'normal'
        describes, if the horizontal direct irradiance or the direct normal
        irradiance is used
    date_col, irradiance_col, t_amb_col: string
        describes the name of the columns in the dataframe df
        defaults: 'date', 'E_dir_hor', 't_amb'

    Returns
    -------
    DataFrame
        The DataFrame will have the following columns:
        col_ira
        eta_c
    right now, the dataframe have more columns to test the function. will be
    removed later

    col_ira: the irradiance on collector after all losses which occur before
    the light hits the collectors surface

    proposal of values
    -------
        if you have no idea, which values your collector have, here are values,
        which were measured in [1] for a collector:
        a1: -0.00159, a2: 0.0000977,
        eta_0: 0.816, c1: 0.0622, c2: 0.00023,

    Reference:
    -------
    [1] Janotte, N; et al: Dynamic performance evaluation of the HelioTrough
    collector demon-stration loop - towards a new benchmark in parabolic
    trough qualification, SolarPACES 2013
    """

    date_time_index = pd.date_range(df.loc[0, date_col], periods=periods,
                                    freq='H', tz=tz)
    datainput = df.iloc[:periods]

    if irradiance == 'horizontal':
        data = pd.DataFrame({'date': date_time_index,
                             'E_dir_hor': datainput[irradiance_col],
                             't_amb': datainput[t_amb_col]})
    elif irradiance == 'normal':
        data = pd.DataFrame({'date': date_time_index,
                             'dni': datainput[irradiance_col],
                             't_amb': datainput[t_amb_col]})

    data.set_index('date', inplace=True)

    solposition = pvlib.solarposition.get_solarposition(
        time=date_time_index,
        latitude=lat,
        longitude=long)
    data['apparent_zenith'] = solposition['apparent_zenith']  # just for information. Can be removed, if it is wanted
    data['azimuth'] = solposition['azimuth']  # just for information. Can be removed, if it is wanted

    tracking_data = pvlib.tracking.singleaxis(
        solposition['apparent_zenith'], solposition['azimuth'],
        axis_tilt=col_tilt, axis_azimuth=col_azimuth)
    data['surface_tilt'] = tracking_data['surface_tilt']  # just for information. Can be removed, if it is wanted
    data['surface_azimuth'] = tracking_data['surface_azimuth']  # just for information. Can be removed, if it is wanted
    data['tracker_theta'] = tracking_data['tracker_theta']  # just for information. Can be removed, if it is wanted
    data['aoi'] = tracking_data['aoi']

    if irradiance == 'horizontal':
        poa_horizontal_ratio = pvlib.irradiance.poa_horizontal_ratio(
            tracking_data['surface_tilt'], tracking_data['surface_azimuth'],
            solposition['apparent_zenith'], solposition['azimuth'])
        data['poa_horizontal_ratio'] = poa_horizontal_ratio # just for information. Can be removed, if it is wanted

        ira_on_col = data['E_dir_hor'] * poa_horizontal_ratio
        data['ira_on_col'] = ira_on_col  # just for information. Can be removed, if it is wanted

    elif irradiance == 'normal':
        ira_on_col = pvlib.irradiance.beam_coponent(
            tracking_data['surface_tilt'], tracking_data['surface_azimuth'],
            solposition['apparent_zenith'], solposition['azimuth'], data['dni']
        )
        data['ira_on_col'] = ira_on_col  # just for information. Can be removed, if it is wanted

    col_ira = calc_col_ira(ira_on_col, x)
    col_ira = col_ira.fillna(0)
    data['col_ira'] = col_ira  # just for information. Can be removed, if it is wanted

    k = calc_k(a1, a2, tracking_data['aoi'])
    data['k'] = k  # just for information. Can be removed, if it is wanted

    eta_c = calc_eta_c(eta_0, c_1, c_2, k,
                       col_inlet_temp, col_outlet_temp, data['t_amb'], col_ira)
    data['eta_c'] = eta_c  # just for information. Can be removed, if it is wanted
    col_heat = col_ira * eta_c
    data['col_heat'] = col_heat
    return data


def calc_col_ira(ira_on_col, x):
    col_ira = ira_on_col * x**1.5
    return col_ira


def calc_k(a1, a2, aoi):
    k = 1 - a1 * abs(aoi) - a2 * aoi**2
    return k


def calc_eta_c(eta_0, c_1, c_2, k,
               col_inlet_temp, col_outlet_temp, t_amb,
               col_ira):
    delta_t = (col_inlet_temp+col_outlet_temp)/2 - t_amb
    eta_c = pd.Series()
    for index, value in col_ira.items():
        if value > 0:
            eta = eta_0 * k[index] - c_1 * delta_t[
                index] / value - c_2 * delta_t[index] ** 2 / value
            if eta > 0:
                eta_c[index] = eta
            else:
                eta_c[index] = 0
        else:
            eta_c[index] = 0
    return eta_c
