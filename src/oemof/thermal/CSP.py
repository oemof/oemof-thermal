"""Defines all functions, which are necessary for the CSP. The solph-component-
facade will be in another file"""

import pvlib
import pandas as pd


def csp_precalc(df, periods,
                lat, long, tz,
                collector_tilt, collector_azimuth, x, a1, a2,
                eta_0, c_1, c_2,
                collector_inlet_temp, collector_outlet_temp,
                irradiance_method='horizontal',
                date_col='date', irradiance_col='E_dir_hor',
                t_amb_col='t_amb'):
    """
    Calculates collectors efficiency and irradiance according to [1] and the
    heat of the thermal collector

    Parameters
    ---------
    :param df: dataframe
        holding values for time, the irradiance and the ambient temperature
    :param periods: numeric
        defines the number of timesteps
    :param lat: numeric, latitude of the location
    :param long: numeric, longitude of the location
    :param tz: string
        pytz timezone of the location
    :param collector_tilt: numeric, the tilt of the collector.
    :param collector_azimuth: numeric
        the azimuth of the collector. Azimuth according to pvlib in decimal
        degrees East of North
    :param x: numeric
        Cleanliness of the collector (between 0 and 1)
    :param a1: numeric, parameter for the incident angle modifier
    :param a2: numeric, parameter for the incident angle modifier
    :param eta_0: numeric
        optical efficiency of the collector
    :param c_1: numeric, thermal loss parameter
    :param c_2: numeric, thermal loss parameter
    :param collector_inlet_temp: numeric or series with length periods
        collectors inlet temperature
    :param collector_outlet_temp: numeric or series with length periods
        collectors outlet temperature
    :param irradiance_method: string, default 'horizontal'
        values: 'horizontal' or 'normal'
        describes, if the horizontal direct irradiance or the direct normal
        irradiance is given and used for Calculation
    :param date_col: string, default: 'date'
        describes the name of the column in the dataframe df
    :param irradiance_col: string, default: 'E_dir_hor'
        describes the name of the column in the dataframe df
    :param t_amb_col: string, default: 't_amb_col'
        describes the name of the column in the dataframe df

    Returns
    -------
    DataFrame
        The DataFrame will have the following columns:
        collector_irradiance
        eta_c
        collector_heat

    collector_irradiance: the irradiance on collector after all losses which
    occur before the light hits the collectors surface

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
    # Creation of input-DF with 3 columns, depending on irradiance_method
    datainput = df.iloc[:periods]

    if irradiance_method == 'horizontal':
        data = pd.DataFrame({'date': date_time_index,
                             'E_dir_hor': datainput[irradiance_col],
                             't_amb': datainput[t_amb_col]})
    elif irradiance_method == 'normal':
        data = pd.DataFrame({'date': date_time_index,
                             'dni': datainput[irradiance_col],
                             't_amb': datainput[t_amb_col]})
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

        irradiance_on_collector = data['E_dir_hor'] * poa_horizontal_ratio

    elif irradiance_method == 'normal':
        irradiance_on_collector = pvlib.irradiance.beam_coponent(
            tracking_data['surface_tilt'], tracking_data['surface_azimuth'],
            solarposition['apparent_zenith'], solarposition['azimuth'],
            data['dni'])

    # Calculation of the irradiance which reaches the collector after all
    # losses (cleaniness)
    collector_irradiance = calc_collector_irradiance(
        irradiance_on_collector, x)
    collector_irradiance = collector_irradiance.fillna(0)
    data['collector_irradiance'] = collector_irradiance

    # Calculation of the incidence angle modifier
    iam = calc_iam(a1, a2, tracking_data['aoi'])

    # Calculation of the collectors efficiency
    eta_c = calc_eta_c(eta_0, c_1, c_2, iam,
                       collector_inlet_temp, collector_outlet_temp,
                       data['t_amb'], collector_irradiance)
    data['eta_c'] = eta_c

    # Calculation of the collectors heat
    collector_heat = collector_irradiance * eta_c
    data['collector_heat'] = collector_heat
    return data


def calc_collector_irradiance(irradiance_on_collector, x):
    """
    Subtractes the losses of dirtiness from the irradiance on the collector
    :param irradiance_on_collector: irradiance which hits collectors surface
    :param x: Cleanliness of the collector (between 0 and 1)
    :return: collector_irradiance (irradiance on collector after all losses)
    """
    collector_irradiance = irradiance_on_collector * x**1.5
    return collector_irradiance


def calc_iam(a1, a2, aoi):
    """
    Calculates the incidence angle modifier
    :param a1: parameter 1 for the incident angle modifier
    :param a2: parameter 2 for the incident angle modifier
    :param aoi: angle of incidence
    :return: incidence angle modifier
    """
    iam = 1 - a1 * abs(aoi) - a2 * aoi**2
    return iam


def calc_eta_c(eta_0, c_1, c_2, iam,
               collector_inlet_temp, collector_outlet_temp, t_amb,
               collector_irradiance):
    """
    Calculates collectors efficiency
    :param eta_0: optical efficiency of the collector
    :param c_1: thermal loss parameter
    :param c_2: thermal loss parameter
    :param iam: incidence angle modifier
    :param collector_inlet_temp: collectors inlet temperature
    :param collector_outlet_temp: collectors outlet temperature
    :param t_amb: ambient temperature
    :param collector_irradiance: irradiance on collector after all losses
    :return: collectors efficiency
    """
    delta_t = (collector_inlet_temp + collector_outlet_temp) / 2 - t_amb
    eta_c = pd.Series()
    for index, value in collector_irradiance.items():
        if value > 0:
            eta = eta_0 * iam[index] - c_1 * delta_t[
                index] / value - c_2 * delta_t[index] ** 2 / value
            if eta > 0:
                eta_c[index] = eta
            else:
                eta_c[index] = 0
        else:
            eta_c[index] = 0
    return eta_c
