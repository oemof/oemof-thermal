import pandas as pd
import oemof.thermal.concentrating_solar_power as csp


def test_calculation_of_collector_irradiance_for_single_value():
    res = csp.calc_collector_irradiance(10, 0.9)

    assert res == 8.5381496824546241963970125


def test_calculation_of_collector_irradiance_for_a_series():
    s = pd.Series([10, 20, 30], index=[1, 2, 3])
    res = csp.calc_collector_irradiance(s, 0.9)
    result = pd.Series(
        [8.5381496824546242, 17.0762993649092484, 25.614449047363873],
        index=[1, 2, 3])
    assert res.eq(result).all()


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
    assert res.eq(result).all()

#
# def test_eta():
#     s = pd.Series([200], index=[0])
#     iam = pd.Series([0.83525], index=[0])
#     ambient = pd.Series([20], index=[0])
#     res = csp.calc_eta_c(0.816, 0.0622, 0.00023, iam, 235, 300, ambient, s,
#                          'Janotte')
#     assert res == pd.Series([0.5341468125], index=[0])
