"""Defines all functions, which are necessary for the CSP. The solph-component-
facade will be in another file"""

import pvlib
import pandas as pd


def csp_precalc(df, periods,
                lat, long, tz,
                collector_tilt, collector_azimuth, x, a_1, a_2,
                eta_0, c_1, c_2,
                temp_collector_inlet, temp_collector_outlet,
                irradiance_method='horizontal',
                date_col='date', irradiance_col='E_dir_hor',
                temp_amb_col='t_amb'):
    """
    Calculates collectors efficiency and irradiance according to [1] and the
    heat of the thermal collector

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
    tz: string
        pytz timezone of the location.
    collector_tilt: numeric
        The tilt of the collector.
    collector_azimuth: numeric
        The azimuth of the collector. Azimuth according to pvlib in decimal
        degrees East of North
    x: numeric
        Cleanliness of the collector (between 0 and 1).
    a_1: numeric
        Parameter for the incident angle modifier.
    a_2: numeric
        Parameter for the incident angle modifier.
    eta_0: numeric
        Optical efficiency of the collector.
    c_1: numeric
        Thermal loss parameter 1.
    c_2: numeric
        Thermal loss parameter 2.
    temp_collector_inlet: numeric or series with length periods
        Collectors inlet temperature.
    temp_collector_outlet: numeric or series with length periods
        Collectors outlet temperature.
    irradiance_method: string, default 'horizontal'
        Valid values are: 'horizontal' or 'normal'. Describes, if the
        horizontal direct irradiance or the direct normal irradiance is
        given and used for calculation.
    date_col: string, default: 'date'
        Describes the name of the column in the dataframe df.
    irradiance_col: string, default: 'E_dir_hor'
        Describes the name of the column in the dataframe df.
    temp_amb_col: string, default: 't_amb_col'
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


    **proposal of values**

    If you have no idea, which values your collector have, here are values,
    which were measured in [1] for a collector:
    a1: -0.00159, a2: 0.0000977,
    eta_0: 0.816, c1: 0.0622, c2: 0.00023.

    **Reference**

    [1] Janotte, N; et al: Dynamic performance evaluation of the HelioTrough \
    collector demon-stration loop - towards a new benchmark in parabolic \
    trough qualification, SolarPACES 2013

    """

    date_time_index = pd.date_range(df.loc[0, date_col], periods=periods,
                                    freq='H', tz=tz)
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

        irradiance_on_collector = data['E_dir_hor'] * poa_horizontal_ratio

    elif irradiance_method == 'normal':
        irradiance_on_collector = pvlib.irradiance.beam_coponent(
            tracking_data['surface_tilt'], tracking_data['surface_azimuth'],
            solarposition['apparent_zenith'], solarposition['azimuth'],
            data['dni'])

    # Calculation of the irradiance which reaches the collector after all
    # losses (cleanliness)
    collector_irradiance = calc_collector_irradiance(
        irradiance_on_collector, x)
    collector_irradiance = collector_irradiance.fillna(0)
    data['collector_irradiance'] = collector_irradiance

    # Calculation of the incidence angle modifier
    iam = calc_iam(a_1, a_2, tracking_data['aoi'])

    # Calculation of the collectors efficiency
    eta_c = calc_eta_c(eta_0, c_1, c_2, iam,
                       temp_collector_inlet, temp_collector_outlet,
                       data['t_amb'], collector_irradiance)
    data['eta_c'] = eta_c

    # Calculation of the collectors heat
    collector_heat = collector_irradiance * eta_c
    data['collector_heat'] = collector_heat

    return data


def calc_collector_irradiance(irradiance_on_collector, x):
    """
    Subtractes the losses of dirtiness from the irradiance on the collector

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
    collector_irradiance = irradiance_on_collector * x**1.5
    return collector_irradiance


def calc_iam(a_1, a_2, aoi):
    """
    Calculates the incidence angle modifier

    Parameters
    ----------
    a_1: numeric
        Parameter 1 for the incident angle modifier.
    a_2: numeric
        Parameter 2 for the incident angle modifier.
    aoi: series of numeric
        Angle of incidence.

    Returns
    -------
    Iicidence angle modifier: series of numeric

    """
    iam = 1 - a_1 * abs(aoi) - a_2 * aoi**2
    return iam


def calc_eta_c(eta_0, c_1, c_2, iam,
               temp_collector_inlet, temp_collector_outlet, temp_amb,
               collector_irradiance):
    """
    Calculates collectors efficiency

    Parameters
    ----------
    eta_0: numeric
        Optical efficiency of the collector.
    c_1: numeric
        Thermal loss parameter 1.
    c_2: numeric
        Thermal loss parameter 2.
    iam: series of numeric
        Incidence angle modifier.
    temp_collector_inlet: numeric, in °C
        Collectors inlet temperature.
    temp_collector_outlet: mumeric, in °C
        Collectors outlet temperature.
    temp_amb: series of numeric, in °C
        Ambient temperature.
    collector_irradiance: series of numeric
        Irradiance on collector after all losses.

    Returns
    -------
    collectors efficiency: series of numeric

    """
    delta_t = (temp_collector_inlet + temp_collector_outlet) / 2 - temp_amb
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
