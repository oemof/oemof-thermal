from oemof.thermal.heat_pipeline import (calculate_investment_cost_per_meter,
                                         calculate_maximal_mass_flow,
                                         calculate_min_max_heat_flow,
                                         calculate_heat_losses_per_meter)

pipe_properties = None
average_flow_velocity = None
diameter = None
temp_inlet = 120  # [deg C]
temp_return = 70  # [deg C]
isolation = None

investment_cost_per_meter = calculate_investment_cost_per_meter(pipe_properties)

maximum_mass_flow = calculate_maximal_mass_flow(average_flow_velocity, diameter)

minimum_heat_flow, maximum_heat_flow = calculate_min_max_heat_flow(temp_inlet, temp_return, maximum_mass_flow)

losses_per_meter = calculate_heat_losses_per_meter(temp_inlet, temp_return, diameter, isolation)

heat_pipeline = oemof.thermal.heat_pipeline.HeatPipeline(
    label='pipe-1',
    inbus=b_heat_0,
    outbus=b_heat_1,
    heat_flow_max=5,
    heat_flow_min=1,
    losses_fixed=0.1
)
