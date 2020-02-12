
#  use environment 'env05'

def calc_characteristic_temp(t_hot, t_cool, t_chill, coef_a, coef_e, method):
    lengths = [len(t_hot), len(t_cool), len(t_chill)]
    length = max(lengths)

    # External mean temperature at generator (g)
    if len(t_hot) == 1:
        list_t_g = t_hot*length  # t_hot[0]*length
    elif len(t_hot) == length:
        list_t_g = t_hot
    else:
        print("")
        print("ERROR - "
              "Length of argument 't_hot' seems not to match requirements")
    # External mean temperature at absorber/condenser (ac)
    if len(t_cool) == 1:
        list_t_ac = t_cool*length
    elif len(t_cool) == length:
        list_t_ac = t_cool
    else:
        print("")
        print("ERROR - "
              "Length of argument 't_cool' seems not to match requirements")
    # External mean temperature at evaporator (e)
    if len(t_chill) == 1:
        list_t_e = t_chill*length
    elif len(t_chill) == length:
        list_t_e = t_chill
    else:
        print("")
        print("ERROR - "
              "Length of argument 't_chill' seems not to match requirements")

    if method == 'kuehn_and_ziegler':
        ddts = [t_g - coef_a*t_ac + coef_e*t_e for
               t_g, t_ac, t_e in zip(list_t_g, list_t_ac, list_t_e)]
    else:
        ddts = None
        print("")
        print("ERROR - Unknown argument 'method'.")
        print("Possible options: 'kuehn_and_ziegler'")
        print("ddt was not calculated!")
        print("")

    return ddts

def calc_heat_flux(ddts, coef_s, coef_r, method):
    if method == 'kuehn_and_ziegler':
        Q_dots = [coef_s*ddt + coef_r for ddt in ddts]
    else:
        Q_dot_evap = None
        print("ERROR - unknown argument 'method'. "
              "Heat flux Q_dot was not calculated!")
    return Q_dots


def define_AC_specs(Q_dots_evap, Q_dots_gen):
    # Define Absorption Chiller specifications
    AC_specs = {
        'COPs': [Q_e/Q_g for Q_e, Q_g in zip(Q_dots_evap, Q_dots_gen)],
        'Q_chill_max': [Q_e/max(Q_dots_evap) for Q_e in Q_dots_evap],  # In %
        'Q_chill_nominal': max(Q_dots_evap)  # Absolute value of max heat flux
    }
    return AC_specs
