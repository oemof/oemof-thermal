import oemof.thermal.absorption_heatpumps_and_chillers as ac
import pytest
import pandas as pd
import os


def test_calc_characteristic_temp_Kuehn():
    """Test characteristic temperature calculation for chiller 'Kuehn'."""
    filename_charpara = os.path.join(
        os.path.dirname(__file__),
        '../examples/absorption_heatpumps_and_chiller/'
        'data/characteristic_parameters.csv')
    charpara = pd.read_csv(filename_charpara)

    chiller_name = 'Kuehn'

    ddt = ac.calc_characteristic_temp(
        t_hot=[85, 85],
        t_cool=[30],
        t_chill=[15],
        coef_a=charpara[(charpara['name'] == chiller_name)]['a'].values[0],
        coef_e=charpara[(charpara['name'] == chiller_name)]['e'].values[0],
        method='kuehn_and_ziegler')
    assert ddt == [37, 37]


def test_calc_characteristic_temp_Braod_01():
    """Test characteristic temperature calculation for chiller 'Broad_01'."""
    filename_charpara = os.path.join(
        os.path.dirname(__file__),
        '../examples/absorption_heatpumps_and_chiller/'
        'data/characteristic_parameters.csv')
    charpara = pd.read_csv(filename_charpara)

    chiller_name = 'Broad_01'
    n = 2
    ddt = ac.calc_characteristic_temp(
        t_hot=[85] * n,
        t_cool=[30],
        t_chill=[15],
        coef_a=charpara[(charpara['name'] == chiller_name)]['a'].values[0],
        coef_e=charpara[(charpara['name'] == chiller_name)]['e'].values[0],
        method='kuehn_and_ziegler')
    assert ddt == [61.45, 61.45]


def test_calc_characteristic_temp_input_list_single_entry():
    """Test if calc_characteristic_temp works with lists of
    length 1 (a single entry) as input for all three temperatures."""
    ddt = ac.calc_characteristic_temp(
        t_hot=[85],
        t_cool=[30],
        t_chill=[15],
        coef_a=2.5,
        coef_e=1.8,
        method='kuehn_and_ziegler')
    assert ddt == [37]


def test_calc_heat_flux_evaporator():
    """Test calculation of cooling capacity for chiller 'Broad_01'."""
    Q_dots_evap = ac.calc_heat_flux(
        ddts=[50],
        coef_s=24.121,
        coef_r=-553.194,
        method='kuehn_and_ziegler')
    assert Q_dots_evap == [652.856]


def test_calc_heat_flux_generator():
    """Test calculation of driving heat for chiller 'Broad_02'."""
    Q_dots_gen = ac.calc_heat_flux(
        ddts=[110],
        coef_s=10.807,
        coef_r=-603.85,
        method='kuehn_and_ziegler')
    assert Q_dots_gen == [584.92]


def test_raised_exception_argument_type():
    """Test if an exception is raised if input argument is not a list."""
    with pytest.raises(TypeError):
        ac.calc_characteristic_temp(
            t_hot=[85],
            t_cool=[30],
            t_chill=[15],
            coef_a=2.5,
            coef_e=1.8,
            method='kuehn_and_ziegler')
