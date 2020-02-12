import numpy as np
from pytest import approx

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
    assert nominal_storage_capacity == 56.62268888888889\
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
    assert loss_rate == 0.00035450164405061065\
        and fixed_losses_relative == 0.00028360131524048847\
        and fixed_losses_absolute == 0.010210176124166827
