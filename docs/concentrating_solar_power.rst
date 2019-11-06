.. _csp_label:

~~~~~~~~~~~~~~~~~~~~~~~~~
Concentrating solar power
~~~~~~~~~~~~~~~~~~~~~~~~~

The precalculations for the concentrating solar power calculate the heat of the
solar collector based on the horizontal direct irradiance or the direct normal
irradiance and information about the collector and the location. The processing
of the irradiance data is done by the pvlib, which calculates the direct
irradiance on the collector. This irradiance is reduced by dust and dirt on the
collector with:

.. math::
    E_{coll} = E_{on_coll} \cdot X^{3/2}

The efficiency on the collector is calculated with

.. math::
    \eta_C = \eta_0 * \kappa(\varTheta) - c_1 \cdot \frac{\Delta T}{E_{coll}}\
    - d_2 \cdot \frac{{\Delta T}^2}{E_{coll}}

    \text{with}

    \kappa(\varTheta) = 1 - a_1 \cdot \vert\varTheta\vert - a_2 * \vert\varTheta\vert^2

In the end, the irradiance on the collector is multiplied with the efficiency
to get the collectors heat. These three values are returned.
Losses, which occur after the heat absorption in the collector (e.g. losses in
pipes) have to be taken into account in the component, which uses the
precalculation (see the example).