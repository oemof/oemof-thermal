# -*- coding: utf-8

"""Test the created constraints against approved constraints.

This file is part of project oemof (github.com/oemof/oemof-thermal).
It's copyrighted by the contributors recorded in the version control
history of the file, available from its original location
oemof-thermal/tests/constraint_tests.py

SPDX-License-Identifier: MIT
"""

import logging
import os
import re

import oemof.solph as solph
import pandas as pd
from oemof.solph import helpers
from pyomo.repn.tests.lp_diff import lp_diff

from oemof.thermal import facades

logging.disable(logging.INFO)


def chop_trailing_whitespace(lines):
    return [re.sub(r"\s*$", "", line) for line in lines]


def remove(pattern, lines):
    if not pattern:
        return lines
    return re.subn(pattern, "", "\n".join(lines))[0].split("\n")


def normalize_to_positive_results(lines):
    negative_result_indices = [
        n for n, line in enumerate(lines) if re.match("^= -", line)
    ]
    equation_start_indices = [
        [n for n in reversed(range(0, nri)) if re.match(".*:$", lines[n])][0]
        + 1
        for nri in negative_result_indices
    ]
    for start, end in zip(equation_start_indices, negative_result_indices):
        for n in range(start, end):
            lines[n] = (
                "-"
                if lines[n] and lines[n][0] == "+"
                else "+" if lines[n] else lines[n]
            ) + lines[n][1:]
        lines[end] = "= " + lines[end][3:]
    return lines


def compare_lp_files(lp_file_1, lp_file_2):
    r"""Compare lp-files to check constraints generated within solph."""
    exp = lp_file_1.read()
    gen = lp_file_2.read()

    # lp_diff returns two arrays of strings with cleaned lp syntax
    # It automatically prints the diff
    exp_diff, gen_diff = lp_diff(exp, gen)

    # sometimes, 0.0 is printed, sometimes 0, harmonise that
    exp_diff = [line + " ".replace(" 0.0 ", " 0 ") for line in exp_diff]
    gen_diff = [line + " ".replace(" 0.0 ", " 0 ") for line in gen_diff]

    assert len(exp_diff) == len(gen_diff)

    # Created the LP files do not have a reproducible
    # order of the lines. Thus, we sort the lines.
    for exp, gen in zip(sorted(exp_diff), sorted(gen_diff)):
        assert exp == gen, "Failed matching expected with generated lp file."


class TestConstraints:

    @classmethod
    def setup_class(cls):
        cls.objective_pattern = re.compile(
            r"^objective.*(?=s\.t\.)", re.DOTALL | re.MULTILINE
        )

        cls.date_time_index = pd.date_range("1/1/2012", periods=3, freq="H")

        cls.tmpdir = helpers.extend_basic_path("tmp")
        logging.info(cls.tmpdir)

    @classmethod
    def setup_method(self):
        self.energysystem = solph.EnergySystem(
            groupings=solph.GROUPINGS, timeindex=self.date_time_index
        )

    def get_om(self):
        return solph.Model(
            self.energysystem, timeindex=self.energysystem.timeindex
        )

    def compare_to_reference_lp(self, ref_filename, my_om=None):
        if my_om is None:
            om = self.get_om()
        else:
            om = my_om

        tmp_filename = ref_filename.replace(".lp", "") + "_tmp.lp"

        new_filepath = os.path.join(self.tmpdir, tmp_filename)

        om.write(new_filepath, io_options={"symbolic_solver_labels": True})

        ref_filepath = os.path.join(
            os.path.dirname(__file__), "lp_files", ref_filename
        )

        with open(new_filepath) as new_file:
            with open(ref_filepath) as ref_file:
                compare_lp_files(new_file, ref_file)

    def test_stratified_thermal_storage_facade(self):
        """Constraint test of a StratifiedThermalStorage without investment."""
        bus_heat = solph.Bus(label="bus_heat")
        self.energysystem.add(bus_heat)

        self.energysystem.add(
            facades.StratifiedThermalStorage(
                label="thermal_storage",
                bus=bus_heat,
                diameter=10,
                height=30,
                temp_h=95,
                temp_c=60,
                temp_env=10,
                u_value=0.5,
                min_storage_level=0.975,
                max_storage_level=0.025,
                capacity=2,
                efficiency=1,
                marginal_cost=0.0001,
            )
        )

        self.compare_to_reference_lp("stratified_thermal_storage.lp")

    def test_stratified_thermal_storage_invest_option_1_facade(self):
        """
        Constraint test of a StratifiedThermalStorage with investment.
        Ratio between capacity and storage_capacity is fixed.
        """
        bus_heat = solph.Bus(label="bus_heat")

        self.energysystem.add(bus_heat)

        self.energysystem.add(
            facades.StratifiedThermalStorage(
                label="thermal_storage",
                bus=bus_heat,
                diameter=10,
                temp_h=95,
                temp_c=60,
                temp_env=10,
                u_value=0.5,
                expandable=True,
                capacity_cost=0,
                storage_capacity_cost=400,
                minimum_storage_capacity=1,
                invest_relation_input_capacity=1 / 6,
                min_storage_level=0.975,
                max_storage_level=0.025,
                efficiency=1,
                marginal_cost=0.0001,
            )
        )

        self.compare_to_reference_lp(
            "stratified_thermal_storage_invest_option_1.lp"
        )

    def test_stratified_thermal_storage_invest_option_2_facade(self):
        """
        Constraint test of a StratifiedThermalStorage with investment.
        Ratio between capacity and storage_capacity is left open.
        """
        bus_heat = solph.Bus(label="bus_heat")
        self.energysystem.add(bus_heat)

        self.energysystem.add(
            facades.StratifiedThermalStorage(
                label="thermal_storage",
                bus=bus_heat,
                diameter=10,
                temp_h=95,
                temp_c=60,
                temp_env=10,
                u_value=0.5,
                expandable=True,
                capacity_cost=50,
                storage_capacity_cost=400,
                minimum_storage_capacity=1,
                min_storage_level=0.975,
                max_storage_level=0.025,
                efficiency=1,
                marginal_cost=0.0001,
            )
        )

        self.compare_to_reference_lp(
            "stratified_thermal_storage_invest_option_2.lp"
        )

    def test_csp_collector_facade(self):
        """Constraint test of a csp collector."""
        bus_heat = solph.Bus(label="bus_heat")
        bus_el = solph.Bus(label="bus_el")

        self.energysystem.add(bus_heat, bus_el)

        d = {
            "Datum": [
                "01.02.2003 09:00",
                "01.02.2003 10:00",
                "01.02.2003 11:00",
            ],
            "E_dir_hor": [43.1, 152.7, 76.9],
            "t_amb": [22.2, 23.2, 24.1],
        }
        input_data = pd.DataFrame(data=d)
        input_data["Datum"] = pd.to_datetime(input_data["Datum"])
        input_data.set_index("Datum", inplace=True)
        input_data.index = input_data.index.tz_localize(tz="Asia/Muscat")

        self.energysystem.add(
            facades.ParabolicTroughCollector(
                label="solar_collector",
                heat_bus=bus_heat,
                electrical_bus=bus_el,
                electrical_consumption=0.05,
                additional_losses=0.2,
                aperture_area=1000,
                loss_method="Janotte",
                irradiance_method="horizontal",
                latitude=23.614328,
                longitude=58.545284,
                collector_tilt=10,
                collector_azimuth=180,
                cleanliness=0.9,
                a_1=-0.00159,
                a_2=0.0000977,
                eta_0=0.816,
                c_1=0.0622,
                c_2=0.00023,
                temp_collector_inlet=435,
                temp_collector_outlet=500,
                temp_amb=input_data["t_amb"],
                irradiance=input_data["E_dir_hor"],
            )
        )

        self.compare_to_reference_lp("csp_collector.lp")

    def test_solar_thermal_collector_facade(self):
        """
        Constraint test of a solar thermal collector.
        """
        bus_heat = solph.Bus(label="bus_heat")
        bus_el = solph.Bus(label="bus_el")

        self.energysystem.add(bus_heat, bus_el)

        d = {
            "Datum": [
                "01.02.2003 09:00",
                "01.02.2003 10:00",
                "01.02.2003 11:00",
            ],
            "global_horizontal_W_m2": [47, 132, 131],
            "diffuse_horizontal_W_m2": [37.57155865, 69.72163199, 98.85021832],
            "temp_amb": [4, 6, 8],
        }
        input_data = pd.DataFrame(data=d)
        input_data["Datum"] = pd.to_datetime(input_data["Datum"])
        input_data.set_index("Datum", inplace=True)
        input_data.index = input_data.index.tz_localize(tz="Europe/Berlin")

        self.energysystem.add(
            facades.SolarThermalCollector(
                label="solar_collector",
                heat_out_bus=bus_heat,
                electricity_in_bus=bus_el,
                electrical_consumption=0.02,
                peripheral_losses=0.05,
                aperture_area=1000,
                latitude=52.2443,
                longitude=10.5594,
                collector_tilt=10,
                collector_azimuth=20,
                eta_0=0.73,
                a_1=1.7,
                a_2=0.016,
                temp_collector_inlet=20,
                delta_temp_n=10,
                irradiance_global=input_data["global_horizontal_W_m2"],
                irradiance_diffuse=input_data["diffuse_horizontal_W_m2"],
                temp_amb=input_data["temp_amb"],
            )
        )

        self.compare_to_reference_lp("solar_thermal_collector.lp")
