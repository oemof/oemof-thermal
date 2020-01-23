import oemof.thermal.compression_heatpumps_and_chillers as cmpr_hp_chllr
import pytest
import pandas as pd


def test_cop_calculation_hp():
    cops_HP = cmpr_hp_chllr.calc_cops(
        temp_high=[40],
        temp_low=[12],
        quality_grade=0.4,
        mode='heat_pump')
    assert cops_HP == [4.473571428571428]


def test_calc_cops_with_Series_01():
    ambient_temp_each_hour = {'01:00': 12, '02:00': 12, '03:00': 12}
    temp_l_series = pd.Series(ambient_temp_each_hour)
    cops_HP = cmpr_hp_chllr.calc_cops(
        temp_high=[40],
        temp_low=temp_l_series,
        quality_grade=0.4,
        mode='heat_pump')
    assert cops_HP == [4.473571428571428, 4.473571428571428, 4.473571428571428]

def test_calc_cops_with_Series_02():
    set_temp_each_hour = {'01:00': 40, '02:00': 40, '03:00': 40}
    temp_h_series = pd.Series(set_temp_each_hour)
    cops_HP = cmpr_hp_chllr.calc_cops(
        temp_high=temp_h_series,
        temp_low=[12],
        quality_grade=0.4,
        mode='heat_pump')
    assert cops_HP == [4.473571428571428, 4.473571428571428, 4.473571428571428]

def test_cop_calculation_hp_list_input_01():
    cops_HP = cmpr_hp_chllr.calc_cops(
        temp_high=[40, 40],
        temp_low=[12],
        quality_grade=0.4,
        mode='heat_pump')
    assert cops_HP == [4.473571428571428, 4.473571428571428]


def test_cop_calculation_hp_list_input_02():
    cops_HP = cmpr_hp_chllr.calc_cops(
        temp_high=[40],
        temp_low=[12, 12],
        quality_grade=0.4,
        mode='heat_pump')
    assert cops_HP == [4.473571428571428, 4.473571428571428]


def test_cop_calculation_airsource_hp_with_icing_01():
    cops_ASHP = cmpr_hp_chllr.calc_cops(
        temp_high=[40],
        temp_low=[1.3],
        quality_grade=0.5,
        mode='heat_pump',
        consider_icing=True,
        temp_threshold_icing=2,
        factor_icing=0.8)
    assert cops_ASHP == [3.236692506459949]


def test_cop_calculation_airsource_hp_with_icing_02():
    cops_ASHP = cmpr_hp_chllr.calc_cops(
        temp_high=[40],
        temp_low=[2.3],
        quality_grade=0.5,
        mode='heat_pump',
        consider_icing=True,
        temp_threshold_icing=2,
        factor_icing=0.8)
    assert cops_ASHP == [4.15318302387268]


def test_cop_calculation_chiller():
    cops_chiller = cmpr_hp_chllr.calc_cops(
        temp_high=[35],
        temp_low=[17],
        quality_grade=0.45,
        mode='chiller')
    assert cops_chiller == [7.25375]


def test_raised_exception_01():
    """Test if an exception is raised if temp_low is not a list."""
    with pytest.raises(TypeError):
        cmpr_hp_chllr.calc_cops(
            temp_high=[40],
            temp_low=12,  # ERROR - temp_low has to be a list!
            quality_grade=0.4,
            mode='heat_pump',
            consider_icing=True,
            temp_threshold_icing=2,
            factor_icing=0.8)


def test_raised_exception_02():
    """Test if an exception is raised if temp_high is not a list."""
    with pytest.raises(TypeError):
        cmpr_hp_chllr.calc_cops(
            temp_high=40,  # ERROR - temp_high has to be a list!
            temp_low=[12],
            quality_grade=0.4,
            mode='heat_pump',
            consider_icing=True,
            temp_threshold_icing=2,
            factor_icing=0.8)


def test_raised_exception_03():
    """Test if an exception is raised if temp_high and
    temp_low have different length AND none of them is of length 1."""
    with pytest.raises(IndexError):
        cmpr_hp_chllr.calc_cops(
            temp_high=[40, 39, 39],
            temp_low=[12, 10],  # ERROR - len(temp_low) has
            # to be 1 or equal to len(temp_high)
            quality_grade=0.4,
            mode='heat_pump',
            consider_icing=True,
            temp_threshold_icing=2,
            factor_icing=0.8)


def test_raised_exception_04():
    """Test if an exception is raised if ... """
    with pytest.raises(ValueError):
        cmpr_hp_chllr.calc_cops(
            temp_high=[39],
            temp_low=[17],
            quality_grade=0.4,
            mode='chiller',
            consider_icing=True,
            temp_threshold_icing=2,
            factor_icing=0.8)


def test_raised_exception_05():
    """Test if an exception is raised if ... """
    with pytest.raises(ValueError):
        cmpr_hp_chllr.calc_cops(
            temp_high=[39],
            temp_low=[17],
            quality_grade=0.4,
            mode='chiller',
            temp_threshold_icing=2,
            factor_icing=0.8)


def test_calc_max_Q_dot_chill():
    nominal_conditions = {
        'nominal_Q_chill': 20,
        'nominal_el_consumption': 5}
    actual_cop = [4.5]
    max_Q_chill = cmpr_hp_chllr.calc_max_Q_dot_chill(nominal_conditions,
                                                     cops=actual_cop)
    assert max_Q_chill == [1.125]


def test_raised_exceptions_05():
    with pytest.raises(TypeError):
        actual_cop = 4.5  # ERROR - has to be of type list!
        nom_cond = {'nominal_Q_chill': 20, 'nominal_el_consumption': 5}
        cmpr_hp_chllr.calc_max_Q_dot_chill(nominal_conditions=nom_cond,
                                           cops=actual_cop)


def test_calc_max_Q_dot_heat():
    nom_cond = {
        'nominal_Q_hot': 20,
        'nominal_el_consumption': 5}
    actual_cop = [4.5]
    max_Q_hot = cmpr_hp_chllr.calc_max_Q_dot_heat(nominal_conditions=nom_cond,
                                                  cops=actual_cop)
    assert max_Q_hot == [1.125]


def test_calc_chiller_quality_grade():
    nom_cond = {
        'nominal_Q_chill': 20,
        'nominal_el_consumption': 5,
        't_high_nominal': 35,
        't_low_nominal': 7}
    q_grade = cmpr_hp_chllr.calc_chiller_quality_grade(nominal_conditions=nom_cond)
    assert q_grade == 0.39978582902016785
