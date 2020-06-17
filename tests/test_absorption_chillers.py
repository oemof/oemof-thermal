import os
import pytest
import pandas as pd
import oemof.thermal.absorption_heatpumps_and_chillers as ac
from pytest import approx


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


def test_calc_characteristic_temp_Braod_02():
    """Test characteristic temperature calculation for chiller 'Broad_02'."""
    filename_charpara = os.path.join(
        os.path.dirname(__file__),
        '../examples/absorption_heatpumps_and_chiller/'
        'data/characteristic_parameters.csv')
    charpara = pd.read_csv(filename_charpara)

    chiller_name = 'Broad_02'
    n = 2
    ddt = ac.calc_characteristic_temp(
        t_hot=[85] * n,
        t_cool=[30],
        t_chill=[15],
        coef_a=charpara[(charpara['name'] == chiller_name)]['a'].values[0],
        coef_e=charpara[(charpara['name'] == chiller_name)]['e'].values[0],
        method='kuehn_and_ziegler')
    assert ddt == [87.625, 87.625]


def test_calc_characteristic_temp_Rotartica():
    """Test characteristic temperature calculation for chiller 'Rotartica'."""
    filename_charpara = os.path.join(
        os.path.dirname(__file__),
        '../examples/absorption_heatpumps_and_chiller/'
        'data/characteristic_parameters.csv')
    charpara = pd.read_csv(filename_charpara)

    chiller_name = 'Rotartica'
    n = 2
    ddt = ac.calc_characteristic_temp(
        t_hot=[85] * n,
        t_cool=[30],
        t_chill=[15],
        coef_a=charpara[(charpara['name'] == chiller_name)]['a'].values[0],
        coef_e=charpara[(charpara['name'] == chiller_name)]['e'].values[0],
        method='kuehn_and_ziegler')
    assert ddt == [approx(32.125), approx(32.125)]


def test_calc_characteristic_temp_Safarik():
    """Test characteristic temperature calculation for chiller 'Safarik'."""
    filename_charpara = os.path.join(
        os.path.dirname(__file__),
        '../examples/absorption_heatpumps_and_chiller/'
        'data/characteristic_parameters.csv')
    charpara = pd.read_csv(filename_charpara)

    chiller_name = 'Safarik'
    n = 2
    ddt = ac.calc_characteristic_temp(
        t_hot=[85] * n,
        t_cool=[30],
        t_chill=[15],
        coef_a=charpara[(charpara['name'] == chiller_name)]['a'].values[0],
        coef_e=charpara[(charpara['name'] == chiller_name)]['e'].values[0],
        method='kuehn_and_ziegler')
    assert ddt == [approx(54.64), approx(54.64)]


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


def test_raised_exception_argument_type_01():
    """Test if an exception is raised if input argument is not a list."""
    with pytest.raises(TypeError):
        ac.calc_characteristic_temp(
            t_hot=85,
            t_cool=[30],
            t_chill=[15],
            coef_a=2.5,
            coef_e=1.8,
            method='kuehn_and_ziegler')


def test_raised_exception_argument_type_02():
    """Test if an exception is raised if input argument is not a list."""
    with pytest.raises(TypeError):
        ac.calc_characteristic_temp(
            t_hot=[85],
            t_cool=30,
            t_chill=[15],
            coef_a=2.5,
            coef_e=1.8,
            method='kuehn_and_ziegler')


def test_raised_exception_argument_type_03():
    """Test if an exception is raised if input argument is not a list."""
    with pytest.raises(TypeError):
        ac.calc_characteristic_temp(
            t_hot=[85],
            t_cool=[30],
            t_chill=15,
            coef_a=2.5,
            coef_e=1.8,
            method='kuehn_and_ziegler')


def test_raised_exception_argument_length_01():
    """Test if an exception is raised if input argument is too long."""
    with pytest.raises(ValueError):
        ac.calc_characteristic_temp(
            t_hot=[85] * 2,
            t_cool=[30] * 3,
            t_chill=[15] * 2,
            coef_a=2.5,
            coef_e=1.8,
            method='kuehn_and_ziegler')


def test_raised_exception_argument_length_02():
    """Test if an exception is raised if input argument is too short."""
    with pytest.raises(ValueError):
        ac.calc_characteristic_temp(
            t_hot=[85] * 3,
            t_cool=[30] * 2,
            t_chill=[15] * 3,
            coef_a=2.5,
            coef_e=1.8,
            method='kuehn_and_ziegler')


def test_raised_exception_method_selection_01():
    """Test if an exception is raised if unknown method name is passed."""
    with pytest.raises(ValueError):
        ac.calc_characteristic_temp(
            t_hot=[85],
            t_cool=[30],
            t_chill=[15],
            coef_a=2.5,
            coef_e=1.8,
            method='shaken_not_stirred')


def test_raised_exception_method_selection_02():
    """Test if an exception is raised if unknown method name is passed."""
    with pytest.raises(ValueError):
        ac.calc_heat_flux(
            ddts=25,
            coef_s=0.42,
            coef_r=0.9,
            method='shaken_not_stirred')
