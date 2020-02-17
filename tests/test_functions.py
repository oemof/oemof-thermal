from oemof.thermal.cogeneration import allocate_emissions


def test_dummy():
    a = 2 * 0.5
    assert a == 1


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
