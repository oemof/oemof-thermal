import numpy as np


# precalculations

def calculate_investment_cost_per_meter(pipe_properties):
    r"""

    Parameters
    ----------
    pipe_properties

    Returns
    -------
    investment_cost_per_meter
    """
    investment_cost_per_meter = None
    return investment_cost_per_meter


def calculate_maximal_mass_flow(average_flow_velocity, diameter):
    r"""

    Parameters
    ----------
    avg_flow_velocity
    diameter

    Returns
    -------

    """
    maximal_mass_flow = None
    return maximal_mass_flow


def calculate_min_max_heat_flow(temp_inlet, temp_return, maximum_mass_flow):
    r"""

    Parameters
    ----------
    temp_inlet
    temp_return
    max_mass_flow

    Returns
    -------

    """
    minimum_heat_flow, maximum_heat_flow = (None, None)
    return minimum_heat_flow, maximum_heat_flow


def calculate_heat_losses_per_meter(temp_inlet, temp_return, diameter, isolation):
    r"""

    Parameters
    ----------
    temp_inlet
    temp_return
    diameter
    isolation

    Returns
    -------
    losses_per_meter
    """
    losses_per_meter = None
    return losses_per_meter


# post-calculations

def calculate_mass_flow(heat_flow, temp_inlet, temp_return):
    r"""

    Calculates the mass flow within a pipe.

    Parameters
    ----------
    heat_flow
    temp_inlet
    temp_return

    Returns
    -------
    mass_flow
    """
    mass_flow = None
    return mass_flow
