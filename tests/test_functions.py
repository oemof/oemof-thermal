import pandas as pd

from oemof.thermal.solar_thermal_collector import (flat_plate_precalc,
                                                   calc_eta_c_flate_plate)


def test_flat_plate_precalc():
    params = {
        'periods': 1,
        'latitude': 52.2443,
        'longitude': 10.5594,
        'timezone': 'Europe/Berlin',
        'collector_tilt': 10,
        'collector_azimuth': 20,
        'eta_0': 0.5,
        'a_1': 1,
        'a_2': 0.5,
        'temp_collector_inlet': 20,
        'delta_temp_n': 10
    }

    # results need to be adjusted
    results = pd.DataFrame({'eta_c': 0.322531, 'collectors_heat': 35.733698})
    data = flat_plate_precalc(params)
    assert data == results


def test_calc_eta_c_flate_plate():
    params = {
        'eta_0': 0.5,
        'a_1': 1,
        'a_2': 0.5,
        'temp_collector_inlet': 20,
        'delta_temp_n': 10,
        'temp_amb': 10,
        'collector_irradiance': 1000,
    }

    assert calc_eta_c_flate_plate(params) == 0.3    # Adjust this value
