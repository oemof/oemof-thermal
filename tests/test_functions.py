import numpy as np
import pandas as pd
from pytest import approx

from oemof.thermal.cogeneration import allocate_emissions
from oemof.thermal.stratified_thermal_storage import (calculate_storage_u_value,
                                                      calculate_storage_dimensions,
                                                      calculate_capacities,
                                                      calculate_losses)


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


def test_allocate_emission_series():
    emissions_dict = {}
    for method in ['iea', 'efficiency', 'finnish']:
        emissions_dict[method] = allocate_emissions(
            total_emissions=pd.Series([200, 200]),
            eta_el=pd.Series([0.3, 0.3]),
            eta_th=pd.Series([0.5, 0.5]),
            method=method,
            eta_el_ref=pd.Series([0.525, 0.525]),
            eta_th_ref=pd.Series([0.82, 0.82])
        )

    default = {
        'iea': (
            pd.Series([75.0, 75.0]),
            pd.Series([125.0, 125.0])
        ),
        'efficiency': (
            pd.Series([125.0, 125.0]),
            pd.Series([75.0, 75.0])
        ),
        'finnish': (
            pd.Series([96.7551622418879, 96.7551622418879]),
            pd.Series([103.24483775811208, 103.24483775811208])
        )}

    for key in default:
        for em_result, em_default in zip(emissions_dict[key], default[key]):
            assert em_result.equals(em_default),\
                f"Result \n{em_result} does not match default \n{em_default}"
