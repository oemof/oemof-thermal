import os

import numpy as np
import pandas as pd
import pytest
from pytest import approx

import oemof.thermal.absorption_heatpumps_and_chillers as ac
import oemof.thermal.compression_heatpumps_and_chillers as cmpr_hp_chllr
import oemof.thermal.concentrating_solar_power as csp
from oemof.thermal.cogeneration import allocate_emissions
from oemof.thermal.solar_thermal_collector import calc_eta_c_flate_plate
from oemof.thermal.solar_thermal_collector import flat_plate_precalc
from oemof.thermal.stratified_thermal_storage import calculate_capacities
from oemof.thermal.stratified_thermal_storage import calculate_losses
from oemof.thermal.stratified_thermal_storage import (
    calculate_storage_dimensions,
)
from oemof.thermal.stratified_thermal_storage import calculate_storage_u_value


def test_cop_calculation_hp():
    cops_HP = cmpr_hp_chllr.calc_cops(
        temp_high=[40], temp_low=[12], quality_grade=0.4, mode="heat_pump"
    )
    assert cops_HP == [4.473571428571428]


def test_calc_cops_with_Series_01():
    ambient_temp_each_hour = {"01:00": 12, "02:00": 12, "03:00": 12}
    temp_l_series = pd.Series(ambient_temp_each_hour)
    cops_HP = cmpr_hp_chllr.calc_cops(
        temp_high=[40],
        temp_low=temp_l_series,
        quality_grade=0.4,
        mode="heat_pump",
    )
    assert cops_HP == [4.473571428571428, 4.473571428571428, 4.473571428571428]


def test_calc_cops_with_Series_02():
    set_temp_each_hour = {"01:00": 40, "02:00": 40, "03:00": 40}
    temp_h_series = pd.Series(set_temp_each_hour)
    cops_HP = cmpr_hp_chllr.calc_cops(
        temp_high=temp_h_series,
        temp_low=[12],
        quality_grade=0.4,
        mode="heat_pump",
    )
    assert cops_HP == [4.473571428571428, 4.473571428571428, 4.473571428571428]


def test_cop_calculation_hp_list_input_01():
    cops_HP = cmpr_hp_chllr.calc_cops(
        temp_high=[40, 40], temp_low=[12], quality_grade=0.4, mode="heat_pump"
    )
    assert cops_HP == [4.473571428571428, 4.473571428571428]


def test_cop_calculation_hp_list_input_02():
    cops_HP = cmpr_hp_chllr.calc_cops(
        temp_high=[40], temp_low=[12, 12], quality_grade=0.4, mode="heat_pump"
    )
    assert cops_HP == [4.473571428571428, 4.473571428571428]


def test_cop_calculation_airsource_hp_with_icing_01():
    cops_ASHP = cmpr_hp_chllr.calc_cops(
        temp_high=[40],
        temp_low=[1.3],
        quality_grade=0.5,
        mode="heat_pump",
        temp_threshold_icing=2,
        factor_icing=0.8,
    )
    assert cops_ASHP == [3.236692506459949]


def test_cop_calculation_airsource_hp_with_icing_02():
    cops_ASHP = cmpr_hp_chllr.calc_cops(
        temp_high=[40],
        temp_low=[2.3],
        quality_grade=0.5,
        mode="heat_pump",
        temp_threshold_icing=2,
        factor_icing=0.8,
    )
    assert cops_ASHP == [4.15318302387268]


def test_cop_calculation_chiller():
    cops_chiller = cmpr_hp_chllr.calc_cops(
        temp_high=[35], temp_low=[17], quality_grade=0.45, mode="chiller"
    )
    assert cops_chiller == [7.25375]


def test_raised_exception_01():
    """Test if an exception is raised if temp_low is not a list."""
    with pytest.raises(TypeError):
        cmpr_hp_chllr.calc_cops(
            temp_high=[40],
            temp_low=12,  # ERROR - temp_low has to be a list!
            quality_grade=0.4,
            mode="heat_pump",
            temp_threshold_icing=2,
            factor_icing=0.8,
        )


def test_raised_exception_02():
    """Test if an exception is raised if temp_high is not a list."""
    with pytest.raises(TypeError):
        cmpr_hp_chllr.calc_cops(
            temp_high=40,  # ERROR - temp_high has to be a list!
            temp_low=[12],
            quality_grade=0.4,
            mode="heat_pump",
            temp_threshold_icing=2,
            factor_icing=0.8,
        )


def test_raised_exception_03():
    """Test if an exception is raised if temp_high and
    temp_low have different length AND none of them is of length 1."""
    with pytest.raises(IndexError):
        cmpr_hp_chllr.calc_cops(
            temp_high=[40, 39, 39],
            temp_low=[12, 10],  # ERROR - len(temp_low) has
            # to be 1 or equal to len(temp_high)
            quality_grade=0.4,
            mode="heat_pump",
            temp_threshold_icing=2,
            factor_icing=0.8,
        )


def test_raised_exception_04():
    """Test if an exception is raised if ..."""
    with pytest.raises(ValueError):
        cmpr_hp_chllr.calc_cops(
            temp_high=[39],
            temp_low=[17],
            quality_grade=0.4,
            mode="chiller",
            temp_threshold_icing=2,
            factor_icing=0.8,
        )


def test_raised_exception_05():
    """Test if an exception is raised if ..."""
    with pytest.raises(ValueError):
        cmpr_hp_chllr.calc_cops(
            temp_high=[39],
            temp_low=[17],
            quality_grade=0.4,
            mode="chiller",
            temp_threshold_icing=2,
            factor_icing=0.8,
        )


def test_calc_max_Q_dot_chill():
    nominal_conditions = {"nominal_Q_chill": 20, "nominal_el_consumption": 5}
    actual_cop = [4.5]
    max_Q_chill = cmpr_hp_chllr.calc_max_Q_dot_chill(
        nominal_conditions, cops=actual_cop
    )
    assert max_Q_chill == [1.125]


def test_raised_exceptions_05():
    with pytest.raises(TypeError):
        actual_cop = 4.5  # ERROR - has to be of type list!
        nom_cond = {"nominal_Q_chill": 20, "nominal_el_consumption": 5}
        cmpr_hp_chllr.calc_max_Q_dot_chill(
            nominal_conditions=nom_cond, cops=actual_cop
        )


def test_calc_max_Q_dot_heat():
    nom_cond = {"nominal_Q_hot": 20, "nominal_el_consumption": 5}
    actual_cop = [4.5]
    max_Q_hot = cmpr_hp_chllr.calc_max_Q_dot_heat(
        nominal_conditions=nom_cond, cops=actual_cop
    )
    assert max_Q_hot == [1.125]


def test_calc_chiller_quality_grade():
    nom_cond = {
        "nominal_Q_chill": 20,
        "nominal_el_consumption": 5,
        "t_high_nominal": 35,
        "t_low_nominal": 7,
    }
    q_grade = cmpr_hp_chllr.calc_chiller_quality_grade(
        nominal_conditions=nom_cond
    )
    assert q_grade == 0.39978582902016785


def test_calculate_storage_u_value():
    params = {
        "s_iso": 50,  # mm
        "lamb_iso": 0.05,  # W/(m*K)
        "alpha_inside": 1,  # W/(m2*K)
        "alpha_outside": 1,  # W/(m2*K)
    }

    u_value = calculate_storage_u_value(**params)
    assert u_value == 1 / 3


def test_calculate_storage_dimensions():
    params = {
        "height": 10,  # m
        "diameter": 10,  # m
    }

    volume, surface = calculate_storage_dimensions(**params)
    assert volume == approx(250 * np.pi) and surface == approx(150 * np.pi)


def test_calculate_capacities():
    params = {
        "volume": 1000,  # m3
        "temp_h": 100,  # deg C
        "temp_c": 50,  # deg C
    }

    nominal_storage_capacity = calculate_capacities(**params)
    assert nominal_storage_capacity == 56.62804059111111


def test_calculate_losses():
    params = {
        "u_value": 1,  # W/(m2*K)
        "diameter": 10,  # m
        "temp_h": 100,  # deg C
        "temp_c": 50,  # deg C
        "temp_env": 10,  # deg C
    }

    loss_rate, fixed_losses_relative, fixed_losses_absolute = calculate_losses(
        **params
    )
    assert (
        loss_rate == 0.0003531819182021882
        and fixed_losses_relative == 0.00028254553456175054
        and fixed_losses_absolute == 0.010210176124166827
    )


def test_allocate_emissions():
    emissions_dict = {}
    for method in ["iea", "efficiency", "finnish"]:
        emissions_dict[method] = allocate_emissions(
            total_emissions=200,
            eta_el=0.3,
            eta_th=0.5,
            method=method,
            eta_el_ref=0.525,
            eta_th_ref=0.82,
        )

    result = {
        "iea": (75.0, 125.0),
        "efficiency": (125.0, 75.0),
        "finnish": (96.7551622418879, 103.24483775811208),
    }

    assert emissions_dict == result


def test_allocate_emission_series():
    emissions_dict = {}
    for method in ["iea", "efficiency", "finnish"]:
        emissions_dict[method] = allocate_emissions(
            total_emissions=pd.Series([200, 200]),
            eta_el=pd.Series([0.3, 0.3]),
            eta_th=pd.Series([0.5, 0.5]),
            method=method,
            eta_el_ref=pd.Series([0.525, 0.525]),
            eta_th_ref=pd.Series([0.82, 0.82]),
        )

    default = {
        "iea": (pd.Series([75.0, 75.0]), pd.Series([125.0, 125.0])),
        "efficiency": (pd.Series([125.0, 125.0]), pd.Series([75.0, 75.0])),
        "finnish": (
            pd.Series([96.7551622418879, 96.7551622418879]),
            pd.Series([103.24483775811208, 103.24483775811208]),
        ),
    }

    for key in default:
        for em_result, em_default in zip(emissions_dict[key], default[key]):
            assert em_result.equals(
                em_default
            ), f"Result \n{em_result} does not match default \n{em_default}"


def test_calculation_of_collector_irradiance():
    s = pd.Series([10, 20, 30], index=[1, 2, 3])
    res = csp.calc_collector_irradiance(s, 0.9)
    result = pd.Series(
        [8.5381496824546242, 17.0762993649092484, 25.614449047363873],
        index=[1, 2, 3],
    )
    assert res.values == approx(result.values)


def test_calculation_iam_for_single_value():
    res = csp.calc_iam(-0.00159, 0.0000977, 0, 0, 0, 0, 50, "Janotte")

    assert res == 0.8352499999999999


def test_calculation_iam_andasol():
    res = csp.calc_iam(
        -8.65e-4,
        8.87e-4,
        -5.425e-5,
        1.665e-6,
        -2.309e-8,
        1.197e-10,
        50,
        "Andasol",
    )

    assert res == 0.5460625000000001


def test_calculation_iam_for_a_series():
    s = pd.Series([10, 20, 30], index=[1, 2, 3])
    res = csp.calc_iam(-0.00159, 0.0000977, 0, 0, 0, 0, s, "Janotte")
    result = pd.Series([1.00613, 0.99272, 0.95977], index=[1, 2, 3])
    assert res.eq(result).all()


def test_csp_different_timeindex():
    r"""
    Test if differing time index raises error.
    """
    E_dir_hor = pd.Series([30, 40], index=[1, 2])
    t_amb = pd.Series([30, 40], index=[2, 3])
    with pytest.raises(IndexError):
        csp.csp_precalc(
            20,
            60,
            10,
            180,
            0.9,
            0.78,
            0.816,
            0.0622,
            235,
            300,
            t_amb,
            -8.65e-4,
            8.87e-4,
            loss_method="Janotte",
            E_dir_hor=E_dir_hor,
        )


def test_csp_wrong_loss_method():
    with pytest.raises(ValueError):
        df = pd.DataFrame(
            data={"date": [1, 2], "E_dir_hor": [30, 40], "t_amb": [30, 40]}
        )
        latitude = 23.614328
        longitude = 58.545284
        collector_tilt = 10
        collector_azimuth = 180
        cleanliness = 0.9
        a_1 = -8.65e-4
        a_2 = 8.87e-4
        eta_0 = 0.78
        c_1 = 0.816
        c_2 = 0.0622
        temp_collector_inlet = 235
        temp_collector_outlet = 300
        csp.csp_precalc(
            latitude,
            longitude,
            collector_tilt,
            collector_azimuth,
            cleanliness,
            eta_0,
            c_1,
            c_2,
            temp_collector_inlet,
            temp_collector_outlet,
            df["t_amb"],
            a_1,
            a_2,
            a_3=0,
            a_4=0,
            a_5=0,
            a_6=0,
            loss_method="quatsch",
        )


def test_eta_janotte():
    s = pd.Series([50], index=[1])
    res = csp.calc_eta_c(
        0.816, 0.0622, 0.00023, 0.95, 235, 300, 30, s, "Janotte"
    )
    result = pd.Series([0.22028124999999987], index=[1])
    assert res.eq(result).all()


def test_eta_andasol():
    s = pd.Series([100], index=[1])
    res = csp.calc_eta_c(0.816, 64, 0.00023, 0.95, 235, 300, 30, s, "Andasol")
    result = pd.Series([0.13519999999999988], index=[1])
    assert res.eq(result).all()


def test_flat_plate_precalc():
    d = {
        "Datum": ["01.01.2003 12:00", "01.01.2003 13:00"],
        "global_horizontal_W_m2": [112, 129],
        "diffuse_horizontal_W_m2": [100.3921648, 93.95959036],
        "temp_amb": [9, 10],
    }

    input_data = pd.DataFrame(data=d)
    input_data["Datum"] = pd.to_datetime(input_data["Datum"])
    input_data.set_index("Datum", inplace=True)
    input_data.index = input_data.index.tz_localize(tz="Europe/Berlin")

    params = {
        "lat": 52.2443,
        "long": 10.5594,
        "collector_tilt": 10,
        "collector_azimuth": 20,
        "eta_0": 0.73,
        "a_1": 1.7,
        "a_2": 0.016,
        "temp_collector_inlet": 20,
        "delta_temp_n": 10,
        "irradiance_global": input_data["global_horizontal_W_m2"],
        "irradiance_diffuse": input_data["diffuse_horizontal_W_m2"],
        "temp_amb": input_data["temp_amb"],
    }
    # Save return value from flat_plate_precalc(...) as data
    data = flat_plate_precalc(**params)

    # Data frame containing separately calculated results
    results = pd.DataFrame(
        {
            "eta_c": [0.32003169094533845, 0.34375125091055275],
            "collectors_heat": [33.37642124, 35.95493984],
        }
    )

    assert data["eta_c"].values == approx(results["eta_c"].values) and data[
        "collectors_heat"
    ].values == approx(results["collectors_heat"].values)


def test_calc_eta_c_flate_plate():
    temp_amb = pd.DataFrame(
        {"date": ["1970-01-01 00:00:00.000000001+01:00"], "temp_amb": [9]}
    )
    temp_amb.set_index("date", inplace=True)

    collector_irradiance = pd.DataFrame(
        {
            "date": ["1970-01-01 00:00:00.000000001+01:00"],
            "poa_global": 99.84226497618872,
        }
    )
    collector_irradiance.set_index("date", inplace=True)

    params = {
        "eta_0": 0.73,
        "a_1": 1.7,
        "a_2": 0.016,
        "temp_collector_inlet": 20,
        "delta_temp_n": 10,
        "temp_amb": temp_amb["temp_amb"],
        "collector_irradiance": collector_irradiance["poa_global"],
    }
    data = calc_eta_c_flate_plate(**params)
    assert data.values == approx(0.30176452266786186)  # Adjust this value


def test_calc_characteristic_temp_Kuehn():
    """Test characteristic temperature calculation for chiller 'Kuehn'."""
    filename_charpara = os.path.join(
        os.path.dirname(__file__),
        "../examples/absorption_heatpump_and_chiller/"
        "data/characteristic_parameters.csv",
    )
    charpara = pd.read_csv(filename_charpara)

    chiller_name = "Kuehn"

    ddt = ac.calc_characteristic_temp(
        t_hot=[85, 85],
        t_cool=[30],
        t_chill=[15],
        coef_a=charpara[(charpara["name"] == chiller_name)]["a"].values[0],
        coef_e=charpara[(charpara["name"] == chiller_name)]["e"].values[0],
        method="kuehn_and_ziegler",
    )
    assert ddt == [37, 37]


def test_calc_characteristic_temp_Braod_01():
    """Test characteristic temperature calculation for chiller 'Broad_01'."""
    filename_charpara = os.path.join(
        os.path.dirname(__file__),
        "../examples/absorption_heatpump_and_chiller/"
        "data/characteristic_parameters.csv",
    )
    charpara = pd.read_csv(filename_charpara)

    chiller_name = "Broad_01"
    n = 2
    ddt = ac.calc_characteristic_temp(
        t_hot=[85] * n,
        t_cool=[30],
        t_chill=[15],
        coef_a=charpara[(charpara["name"] == chiller_name)]["a"].values[0],
        coef_e=charpara[(charpara["name"] == chiller_name)]["e"].values[0],
        method="kuehn_and_ziegler",
    )
    assert ddt == [61.45, 61.45]


def test_calc_characteristic_temp_Braod_02():
    """Test characteristic temperature calculation for chiller 'Broad_02'."""
    filename_charpara = os.path.join(
        os.path.dirname(__file__),
        "../examples/absorption_heatpump_and_chiller/"
        "data/characteristic_parameters.csv",
    )
    charpara = pd.read_csv(filename_charpara)

    chiller_name = "Broad_02"
    n = 2
    ddt = ac.calc_characteristic_temp(
        t_hot=[85] * n,
        t_cool=[30],
        t_chill=[15],
        coef_a=charpara[(charpara["name"] == chiller_name)]["a"].values[0],
        coef_e=charpara[(charpara["name"] == chiller_name)]["e"].values[0],
        method="kuehn_and_ziegler",
    )
    assert ddt == [87.625, 87.625]


def test_calc_characteristic_temp_Rotartica():
    """Test characteristic temperature calculation for chiller 'Rotartica'."""
    filename_charpara = os.path.join(
        os.path.dirname(__file__),
        "../examples/absorption_heatpump_and_chiller/"
        "data/characteristic_parameters.csv",
    )
    charpara = pd.read_csv(filename_charpara)

    chiller_name = "Rotartica"
    n = 2
    ddt = ac.calc_characteristic_temp(
        t_hot=[85] * n,
        t_cool=[30],
        t_chill=[15],
        coef_a=charpara[(charpara["name"] == chiller_name)]["a"].values[0],
        coef_e=charpara[(charpara["name"] == chiller_name)]["e"].values[0],
        method="kuehn_and_ziegler",
    )
    assert ddt == [approx(32.125), approx(32.125)]


def test_calc_characteristic_temp_Safarik():
    """Test characteristic temperature calculation for chiller 'Safarik'."""
    filename_charpara = os.path.join(
        os.path.dirname(__file__),
        "../examples/absorption_heatpump_and_chiller/"
        "data/characteristic_parameters.csv",
    )
    charpara = pd.read_csv(filename_charpara)

    chiller_name = "Safarik"
    n = 2
    ddt = ac.calc_characteristic_temp(
        t_hot=[85] * n,
        t_cool=[30],
        t_chill=[15],
        coef_a=charpara[(charpara["name"] == chiller_name)]["a"].values[0],
        coef_e=charpara[(charpara["name"] == chiller_name)]["e"].values[0],
        method="kuehn_and_ziegler",
    )
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
        method="kuehn_and_ziegler",
    )
    assert ddt == [37]


def test_calc_heat_flux_evaporator():
    """Test calculation of cooling capacity for chiller 'Broad_01'."""
    Q_dots_evap = ac.calc_heat_flux(
        ddts=[50], coef_s=24.121, coef_r=-553.194, method="kuehn_and_ziegler"
    )
    assert Q_dots_evap == [652.856]


def test_calc_heat_flux_generator():
    """Test calculation of driving heat for chiller 'Broad_02'."""
    Q_dots_gen = ac.calc_heat_flux(
        ddts=[110], coef_s=10.807, coef_r=-603.85, method="kuehn_and_ziegler"
    )
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
            method="kuehn_and_ziegler",
        )


def test_raised_exception_argument_type_02():
    """Test if an exception is raised if input argument is not a list."""
    with pytest.raises(TypeError):
        ac.calc_characteristic_temp(
            t_hot=[85],
            t_cool=30,
            t_chill=[15],
            coef_a=2.5,
            coef_e=1.8,
            method="kuehn_and_ziegler",
        )


def test_raised_exception_argument_type_03():
    """Test if an exception is raised if input argument is not a list."""
    with pytest.raises(TypeError):
        ac.calc_characteristic_temp(
            t_hot=[85],
            t_cool=[30],
            t_chill=15,
            coef_a=2.5,
            coef_e=1.8,
            method="kuehn_and_ziegler",
        )


def test_raised_exception_argument_length_01():
    """Test if an exception is raised if input argument is too long."""
    with pytest.raises(ValueError):
        ac.calc_characteristic_temp(
            t_hot=[85] * 2,
            t_cool=[30] * 3,
            t_chill=[15] * 2,
            coef_a=2.5,
            coef_e=1.8,
            method="kuehn_and_ziegler",
        )


def test_raised_exception_argument_length_02():
    """Test if an exception is raised if input argument is too short."""
    with pytest.raises(ValueError):
        ac.calc_characteristic_temp(
            t_hot=[85] * 3,
            t_cool=[30] * 2,
            t_chill=[15] * 3,
            coef_a=2.5,
            coef_e=1.8,
            method="kuehn_and_ziegler",
        )


def test_raised_exception_method_selection_01():
    """Test if an exception is raised if unknown method name is passed."""
    with pytest.raises(ValueError):
        ac.calc_characteristic_temp(
            t_hot=[85],
            t_cool=[30],
            t_chill=[15],
            coef_a=2.5,
            coef_e=1.8,
            method="shaken_not_stirred",
        )


def test_raised_exception_method_selection_02():
    """Test if an exception is raised if unknown method name is passed."""
    with pytest.raises(ValueError):
        ac.calc_heat_flux(
            ddts=25, coef_s=0.42, coef_r=0.9, method="shaken_not_stirred"
        )
