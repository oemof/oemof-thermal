import numpy as np
import pandas as pd
from pytest import approx

from oemof.thermal.chp import allocate_emissions
from oemof.thermal.stratified_thermal_storage import (calculate_storage_u_value,
                                                      calculate_storage_dimensions,
                                                      calculate_capacities,
                                                      calculate_losses)
from oemof.thermal.solar_thermal_collector import (flat_plate_precalc,
                                                   calc_eta_c_flate_plate)


def test_calculate_storage_u_value():
    params = {
        's_iso': 50,  # mm
        'lamb_iso': 0.05,  # W/(m*K)
        'alpha_inside': 1,  # W/(m2*K)
        'alpha_outside': 1  # W/(m2*K)
    }

    u_value = calculate_storage_u_value(**params)
    assert u_value == 1 / 3


def test_calculate_storage_dimensions():
    params = {
        'height': 10,  # m
        'diameter': 10,  # m
    }

    volume, surface = calculate_storage_dimensions(**params)
    assert volume == approx(250 * np.pi) and surface == approx(150 * np.pi)


def test_calculate_capacities():
    params = {
        'volume': 1000,  # m3
        'temp_h': 100,  # deg C
        'temp_c': 50,  # deg C
        'nonusable_storage_volume': 0.1,  # dimensionless
    }

    nominal_storage_capacity, max_storage_level, min_storage_level = calculate_capacities(**params)
    assert nominal_storage_capacity == 56.62804059111111\
        and max_storage_level == 0.95\
        and min_storage_level == 0.05


def test_calculate_losses():
    params = {
        'u_value': 1,  # W/(m2*K)
        'diameter': 10,  # m
        'temp_h': 100,  # deg C
        'temp_c': 50,  # deg C
        'temp_env': 10,  # deg C
    }

    loss_rate, fixed_losses_relative, fixed_losses_absolute = calculate_losses(**params)
    assert loss_rate == 0.0003531819182021882\
        and fixed_losses_relative == 0.00028254553456175054\
        and fixed_losses_absolute == 0.010210176124166827


def test_allocate_emissions():
    emissions_dict = {}
    for method in ['iea', 'efficiency', 'finnish']:
        emissions_dict[method] = allocate_emissions(
            total_emissions=200,
            eta_el=0.3,
            eta_th=0.5,
            method=method,
            eta_el_ref=0.525,
            eta_th_ref=0.82
        )

    result = {
        'iea': (75.0, 125.0),
        'efficiency': (125.0, 75.0),
        'finnish': (96.7551622418879, 103.24483775811208)}

    assert emissions_dict == result


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

    collector_irradiance = pd.DataFrame({'date': ['1970-01-01 00:00:00.000000001+01:00'],
                                         'poa_global': 99.84226497618872})
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
    assert data.values == approx(0.30176452266786186)    # Adjust this value
