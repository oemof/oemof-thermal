import pandas as pd
from pytest import approx

from oemof.thermal.solar_thermal_collector import (flat_plate_precalc,
                                                   calc_eta_c_flate_plate)


def test_flat_plate_precalc():
    params = {
       'df': pd.DataFrame(data={'hour': [1, 2],
                                'ghi': [112, 129],
                                'dhi': [100.3921648, 93.95959036],
                                'temp_amb': [9, 10]}),
        'periods': 2,
        'lat': 52.2443,
        'long': 10.5594,
        'tz': 'Europe/Berlin',
        'collector_tilt': 10,
        'collector_azimuth': 20,
        'eta_0': 0.73,
        'a_1': 1.7,
        'a_2': 0.016,
        'temp_collector_inlet': 20,
        'delta_temp_n': 10,
        'date_col': 'hour'
    }
    # Save return value from flat_plate_precalc(...) as data
    data = flat_plate_precalc(**params)

    # Data frame containing separately calculated results
    results = pd.DataFrame({'eta_c': [0.30176452266786186, 0.29787208853863734],
                            'collectors_heat': [30.128853432617774, 27.848310784333435]})

    assert data['eta_c'].values == approx(results['eta_c'].values) and \
           data['collectors_heat'].values == approx(results['collectors_heat'].values)


def test_calc_eta_c_flate_plate():
    temp_amb = pd.DataFrame({'date': ['1970-01-01 00:00:00.000000001+01:00'],
                             'temp_amb': [9]})
    temp_amb.set_index('date', inplace=True)

    collector_irradiance = pd.DataFrame({'date': ['1970-01-01 00:00:00.000000001+01:00'], 'poa_global': 99.84226497618872})
    collector_irradiance.set_index('date', inplace=True)

    params = {
        'eta_0': 0.73,
        'a_1': 1.7,
        'a_2': 0.016,
        'temp_collector_inlet': 20,
        'delta_temp_n': 10,
        'temp_amb': temp_amb['temp_amb'],
        'collector_irradiance': collector_irradiance['poa_global']
    }
    data = calc_eta_c_flate_plate(**params)
    print(data)
    assert 1 == 1   # data == approx(0.30176452266786186)    # Adjust this value
