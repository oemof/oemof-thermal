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
from difflib import unified_diff

import pandas as pd

from oemof.thermal import facades
from oemof.network import Node
from oemof.tools import helpers
import oemof.solph as solph


logging.disable(logging.INFO)


def chop_trailing_whitespace(lines):
    return [re.sub(r'\s*$', '', l) for l in lines]


def remove(pattern, lines):
    if not pattern:
        return lines
    return re.subn(pattern, "", "\n".join(lines))[0].split("\n")


def normalize_to_positive_results(lines):
    negative_result_indices = [
        n for n, line in enumerate(lines)
        if re.match("^= -", line)]
    equation_start_indices = [
        [n for n in reversed(range(0, nri))
         if re.match('.*:$', lines[n])][0] + 1
        for nri in negative_result_indices]
    for (start, end) in zip(
            equation_start_indices,
            negative_result_indices):
        for n in range(start, end):
            lines[n] = (
                '-'
                if lines[n] and lines[n][0] == '+'
                else '+'
                if lines[n]
                else lines[n]) + lines[n][1:]
        lines[end] = '= ' + lines[end][3:]
    return lines


def compare_lp_files(lp_file_1, lp_file_2, ignored=None):
    lines_1 = remove(ignored, chop_trailing_whitespace(lp_file_1.readlines()))
    lines_2 = remove(ignored, chop_trailing_whitespace(lp_file_2.readlines()))

    lines_1 = normalize_to_positive_results(lines_1)
    lines_2 = normalize_to_positive_results(lines_2)

    if not lines_1 == lines_2:
        raise AssertionError(
            "Failed matching lp_file_1 with lp_file_2:\n"
            + "\n".join(
                unified_diff(
                    lines_1,
                    lines_2,
                    fromfile=os.path.relpath(
                        lp_file_1.name),
                    tofile=os.path.basename(
                        lp_file_2.name),
                    lineterm=""
                )
            ))


class TestConstraints:

    @classmethod
    def setup_class(self):
        self.objective_pattern = re.compile(r'^objective.*(?=s\.t\.)',
                                            re.DOTALL | re.MULTILINE)

        self.date_time_index = pd.date_range('1/1/2012', periods=3, freq='H')

        self.tmppath = helpers.extend_basic_path('tmp')
        logging.info(self.tmppath)

    def setup(self):
        self.energysystem = solph.EnergySystem(groupings=solph.GROUPINGS,
                                               timeindex=self.date_time_index)
        Node.registry = self.energysystem

    def get_om(self):
        return solph.Model(self.energysystem,
                           timeindex=self.energysystem.timeindex)

    def test_stratified_thermal_storage_facade(self):
        """Constraint test of a StratifiedThermalStorage without investment.
        """
        bus_heat = solph.Bus(label='bus_heat')

        facades.StratifiedThermalStorage(
            label='thermal_storage',
            bus=bus_heat,
            carrier='water',
            tech='sensible_heat_storage',
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
            marginal_cost=0.0001
        )

        compare_lp_files('stratified_thermal_storage.lp')

    def test_stratified_thermal_storage_invest_facade(self):
        """Constraint test of a StratifiedThermalStorage with investment.
        """
        bus_heat = solph.Bus(label='bus_heat')

        facades.StratifiedThermalStorage(
            label='thermal_storage',
            bus=bus_heat,
            carrier='water',
            tech='sensible_heat_storage',
            diameter=10,
            temp_h=95,
            temp_c=60,
            temp_env=10,
            u_value=0.5,
            expandable=True,
            storage_capacity_cost=400,
            capacity=2,
            min_storage_level=0.975,
            max_storage_level=0.025,
            efficiency=1,
            marginal_cost=0.0001
        )

        compare_lp_files('stratified_thermal_storage_invest.lp')
