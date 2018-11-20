# -*- coding: utf-8 -*-
import pandas as pd

def get_cop(heatbuilding, heatpump_type = "Air", water_temp = 60):
    """ Calculation of the coefficient of performance depending
    on the outside temperature
    
    Parameters
    ----------
    heatbuilding: object
        HeatBuilding object from demandlib.bdew countaining the index 
        and outside temperature
    heatpump_type: string
        defines the technology used. Ground is more efficient than Air.
    water_temp: int
        temperature needed for the heating system
        
    References
    ----------
    ..  [1]: 'https://www.researchgate.net/publication/255759857_A_review_of_domestic_heat_pumps'
        Research paper about domestic heatpumps, containing the formulas used
    """

    cop_lst = []
    
    if heatpump_type == "Air":
        for tmp in heatbuilding.temperature:
            cop = (6.81 - 0.121 * (water_temp - tmp)
                   + 0.00063 * (water_temp - tmp)**2)
            cop_lst.append(cop)
    
    elif heatpump_type == "Ground":
        for tmp in heatbuilding.temperature:
            cop = (8.77 - 0.15 * (water_temp - tmp)
                   + 0.000734 * (water_temp - tmp)**2)
            cop_lst.append(cop)
    
    else:
        # TODO Raise Error
        print("Heatpump type is not defined")
        return None

    heatbuilding.cop = pd.DataFrame({"cop" : cop_lst})
    heatbuilding.cop.set_index(heatbuilding.df.index, inplace = True)

            
    return heatbuilding.cop
