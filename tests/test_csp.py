import pandas as pd
from pytest import approx
import pytest
import oemof.thermal.concentrating_solar_power as csp


def test_calculation_of_collector_irradiance():
    s = pd.Series([10, 20, 30], index=[1, 2, 3])
    res = csp.calc_collector_irradiance(s, 0.9)
    result = pd.Series(
        [8.5381496824546242, 17.0762993649092484, 25.614449047363873],
        index=[1, 2, 3])
    assert res.values == approx(result.values)


def test_calculation_iam_for_single_value():
    res = csp.calc_iam(-0.00159, 0.0000977, 0, 0, 0, 0, 50, 'Janotte')

    assert res == 0.8352499999999999


def test_calculation_iam_andasol():
    res = csp.calc_iam(-8.65e-4, 8.87e-4, -5.425e-5, 1.665e-6, -2.309e-8,
                       1.197e-10, 50, 'Andasol')

    assert res == 0.5460625000000001


def test_calculation_iam_for_a_series():
    s = pd.Series([10, 20, 30], index=[1, 2, 3])
    res = csp.calc_iam(-0.00159, 0.0000977, 0, 0, 0, 0, s, 'Janotte')
    result = pd.Series([1.00613, 0.99272, 0.95977], index=[1, 2, 3])
    assert res.values == approx(result.values)


with pytest.raises(ValueError):
    df = pd.DataFrame(data={'date': ['1/1/2001', '1/2/2001'], 'E_dir_hor': [
        30, 40], 't_amb': [30, 40]})
    latitude = 23.614328
    longitude = 58.545284
    timezone = 'Asia/Muscat'
    collector_tilt = 10
    collector_azimuth = 180
    cleanliness = 0.9
    a_1 = -8.65e-4
    a_2 = 8.87e-4
    a_3 = -5.425e-5
    a_4 = 1.665e-6
    a_5 = -2.309e-8
    a_6 = 1.197e-10
    eta_0 = 0.78
    c_1 = 0.816
    c_2 = 0.0622
    temp_collector_inlet = 235
    temp_collector_outlet = 300
    csp.csp_precalc(latitude, longitude,
                    collector_tilt, collector_azimuth, cleanliness,
                    eta_0, c_1, c_2,
                    temp_collector_inlet, temp_collector_outlet, df['t_amb'],
                    a_1, a_2, a_3=0, a_4=0, a_5=0, a_6=0,
                    loss_method='quatsch')


def test_eta_janotte():
    s = pd.Series([50], index=[1])
    res = csp.calc_eta_c(0.816, 0.0622, 0.00023, 0.95, 235, 300, 30, s,
                         'Janotte')
    result = pd.Series([0.22028124999999987], index=[1])
    assert res.values == approx(result.values)


def test_eta_andasol():
    s = pd.Series([100], index=[1])
    res = csp.calc_eta_c(0.816, 64, 0.00023, 0.95, 235, 300, 30, s,
                         'Andasol')
    result = pd.Series([0.13519999999999988], index=[1])
    assert res.values == approx(result.values)
