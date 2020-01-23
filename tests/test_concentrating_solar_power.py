import pandas as pd
import oemof.thermal.concentrating_solar_power as csp


def test_calculation_of_collector_irradiance_for_single_value():
    res = csp.calc_collector_irradiance(10, 0.9)

    assert res == 8.5381496824546241963970125


def test_calculation_of_collector_irradiance_for_a_Series():
    s = pd.Series([10, 20, 30], index=[1, 2, 3])
    res = csp.calc_collector_irradiance(s, 0.9)
    result = pd.Series(
        [8.5381496824546242, 17.0762993649092484, 25.614449047363873],
        index=[1, 2, 3])
    assert res.eq(result).all()


def test_calculation_iam_for_single_value():
    res = csp.calc_iam(-0.00159, 0.0000977, 50)

    assert res == 0.8352499999999999


def test_calculation_iam_for_a_Series():
    s = pd.Series([10, 20, 30], index=[1, 2, 3])
    res = csp.calc_iam(-0.00159, 0.0000977, s)
    result = pd.Series([1.00613, 0.99272, 0.95977], index=[1, 2, 3])
    assert res.eq(result).all()
