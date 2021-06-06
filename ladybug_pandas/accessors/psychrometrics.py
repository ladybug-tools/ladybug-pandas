from typing import Union

import pandas as pd

from ladybug import psychrometrics
from ladybug.datatype import TYPESDICT

from ..extension_types.arraytype import LadybugArrayType
from ..extension_types.dtype import LadybugDType


@pd.api.extensions.register_dataframe_accessor("psychro")
class PsychrometricsAccessor:

    """A pandas Dataframe accessor to perform psychrometric calculation operations

        Use this "psychro" accessor and pass in the name of a column in your dataframe, 
        a Series or an int/float value to perform as psychormetric operation and return a Series.

    Warning:
        If using a Dataframe column or a Series you must ensure that it is an instance
        of a LadybugArrayType. This is because the Psychrometric accessor runs type checks
        to convert a data type to the right unit if necessary.

    Example:
        .. code-block:: python

        import ladybug_pandas as lbp
        from ladybug.epw import EPW

        epw_path = 'tests/assets/epw/tokyo.epw'

        epw = EPW(epw_path)

        df = lbp.dataframe_from_epw(epw)

        df['Humidity Ratio'] = df.psychro.humid_ratio_from_db_rh(
            db_temp='Dry Bulb Temperature',
            rel_humid='Relative Humidity'
        )

    """

    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def _build_psychro_function(self, function, input_kwargs, output_type, output_unit, **kwargs):

        input_df = pd.DataFrame()

        function_inputs = {}

        for k, v in input_kwargs.items():
            input_value = kwargs.get(k)
            if isinstance(input_value, str):
                series = self._obj[input_value]
                input_type = TYPESDICT[v['input_type']]
                assert isinstance(series.values.dtype.data_type, input_type), \
                    f'Cannot use array of type {series.values.dtype.data_type} for {k}. Must be a {v["input_type"]}'

                input_df[k] = series.values.to_unit(v['input_unit'])

            elif isinstance(input_value, float) or isinstance(input_value, int):
                function_inputs[k] = input_value

        values = []

        if len(input_df) == 0:
            values.append(function(**function_inputs))
        else:
            for _, row in input_df.iterrows():
                function_inputs.update(row.to_dict())
                values.append(function(**function_inputs))

        dtype = LadybugDType(TYPESDICT[output_type](), output_unit)

        return pd.Series(
            data=LadybugArrayType(values, dtype),
            index=self._obj.index,
        )

    def saturated_vapor_pressure(self, t_kelvin: Union[str, float, int, LadybugArrayType]) -> pd.Series:

        return self._build_psychro_function(
            function=psychrometrics.saturated_vapor_pressure,
            input_kwargs={
                't_kelvin': {
                    'input_type': 'Temperature',
                    'input_unit': 'K'
                },
            },
            output_type='Pressure',
            output_unit='Pa',
            t_kelvin=t_kelvin
        )

    def humid_ratio_from_db_rh(self, db_temp, rel_humid, b_press=101325):
        """Humidity ratio (kg water/kg air) from air temperature (C) and relative humidity (%).

        Args:
            db_temp: Dry bulb temperature (C).
            rel_humid: Relative humidity (%).
            b_press: Air pressure (Pa). Default is pressure at sea level (101325 Pa).

        Returns:
            Humidity ratio (kg water/kg air).

        Note:
            [1] ASHRAE Handbook - Fundamentals (2017) ch. 1 eqn 20

            [2] Meyer et al., (2019). PsychroLib: a library of psychrometric
            functions to calculate thermodynamic properties of air. Journal of
            Open Source Software, 4(33), 1137, https://doi.org/10.21105/joss.01137
            https://github.com/psychrometrics/psychrolib/blob/master/src/python/psychrolib.py
        """
        return self._build_psychro_function(
            function=psychrometrics.humid_ratio_from_db_rh,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'rel_humid': {
                    'input_type': 'RelativeHumidity',
                    'input_unit': '%'
                },
                'b_press': {
                    'input_type': 'Pressure',
                    'input_unit': 'Pa'
                }
            },
            output_type='HumidityRatio',
            output_unit='%',
            db_temp=db_temp,
            rel_humid=rel_humid,
            b_press=b_press,
        )

    def enthalpy_from_db_hr(self, db_temp, humid_ratio, reference_temp=0):
        """Enthalpy (kJ/kg) at a given humidity ratio (water/air) and dry bulb temperature (C).

        Args:
            db_temp: Dry bulb temperature (C).
            humid_ratio: Humidity ratio (kg water/kg air).
            reference_temp: Reference dry air temperature (C). Default is 0C,
                which is standard practice for SI enthalpy values. However, for
                IP enthalpy, this is typically at 0F (-17.78C). Alternatively, for
                aboslute thermodynamic enthalpy, one can input 0K (-273.15).

        Returns:
            Enthalpy (kJ/kg).

        Note:
            [1] ASHRAE Handbook - Fundamentals (2017) ch. 1 eqn 30

            [2] Meyer et al., (2019). PsychroLib: a library of psychrometric
            functions to calculate thermodynamic properties of air. Journal of
            Open Source Software, 4(33), 1137, https://doi.org/10.21105/joss.01137
            https://github.com/psychrometrics/psychrolib/blob/master/src/python/psychrolib.py
        """
        return self._build_psychro_function(
            function=psychrometrics.enthalpy_from_db_hr,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'humid_ratio': {
                    'input_type': 'HumidityRatio',
                    'input_unit': '%'
                },
                'reference_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                }
            },
            output_type='Enthalpy',
            output_unit='kJ/kg',
            db_temp=db_temp,
            humid_ratio=humid_ratio,
            reference_temp=reference_temp,
        )

    def dew_point_from_db_rh(self, db_temp, rel_humid):
        """Dew point temperature (C) from air temperature (C) and relative humidity (%).

        The dew point temperature is solved by inverting the equation giving water vapor
        pressure at saturation from temperature, which is relatively slow but ensures
        high accuracy down to 0.1 C at a wide range of dry bulb temperatures.
        The Newton-Raphson (NR) method is used on the logarithm of water vapour
        pressure as a function of temperature, which is a very smooth function
        Convergence is usually achieved in 3 to 5 iterations.

        Args:
            db_temp: Dry bulb temperature (C).
            rel_humid: Relative humidity (%).

        Returns:
            Dew point temperature (C).

        Note:
            [1] ASHRAE Handbook - Fundamentals (2017) ch. 1 eqn. 5 and 6

            [2] Meyer et al., (2019). PsychroLib: a library of psychrometric
            functions to calculate thermodynamic properties of air. Journal of
            Open Source Software, 4(33), 1137, https://doi.org/10.21105/joss.01137
            https://github.com/psychrometrics/psychrolib/blob/master/src/python/psychrolib.py
        """
        return self._build_psychro_function(
            function=psychrometrics.dew_point_from_db_rh,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'rel_humid': {
                    'input_type': 'RelativeHumidity',
                    'input_unit': '%'
                }
            },
            output_type='DewPointTemperature',
            output_unit='C',
            db_temp=db_temp,
            rel_humid=rel_humid,
        )

    def wet_bulb_from_db_rh(self, db_temp, rel_humid, b_press=101325):
        """Wet bulb temperature (C) from air temperature (C) and relative humidity (%).

        Args:
            db_temp: Dry bulb temperature (C).
            rel_humid: Relative humidity (%).
            b_press: Air pressure (Pa). Default is pressure at sea level (101325 Pa).

        Returns:
            Wet bulb temperature (C).

        Note:
            [1] ASHRAE Handbook - Fundamentals (2017) ch. 1 eqn 33 and 35

            [2] Meyer et al., (2019). PsychroLib: a library of psychrometric
            functions to calculate thermodynamic properties of air. Journal of
            Open Source Software, 4(33), 1137, https://doi.org/10.21105/joss.01137
            https://github.com/psychrometrics/psychrolib/blob/master/src/python/psychrolib.py
        """
        return self._build_psychro_function(
            function=psychrometrics.wet_bulb_from_db_rh,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'rel_humid': {
                    'input_type': 'RelativeHumidity',
                    'input_unit': '%'
                },
                'b_press': {
                    'input_type': 'Pressure',
                    'input_unit': 'Pa'
                }
            },
            output_type='WetBulbTemperature',
            output_unit='C',
            db_temp=db_temp,
            rel_humid=rel_humid,
            b_press=b_press,
        )

    def rel_humid_from_db_hr(self, db_temp, humid_ratio, b_press=101325):
        """Relative Humidity (%) from humidity ratio (water/air) and air temperature (C).

        Args:
            db_temp: Dry bulb temperature (C).
            humid_ratio: Humidity ratio (kg water/kg air).
            b_press: Air pressure (Pa). Default is pressure at sea level (101325 Pa).

        Returns:
            Relative humidity (%).
        """
        return self._build_psychro_function(
            function=psychrometrics.rel_humid_from_db_hr,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'humid_ratio': {
                    'input_type': 'HumidityRatio',
                    'input_unit': '%'
                },
                'b_press': {
                    'input_type': 'Pressure',
                    'input_unit': 'Pa'
                }
            },
            output_type='RelativeHumidity',
            output_unit='%',
            db_temp=db_temp,
            humid_ratio=humid_ratio,
            b_press=b_press,
        )

    def rel_humid_from_db_enth(self, db_temp, enthalpy, b_press=101325, reference_temp=0):
        """Relative Humidity (%) from air temperature (C) and enthalpy (kJ/kg).

        Args:
            db_temp: Dry bulb temperature (C).
            enthalpy: Enthalpy (kJ/kg).
            b_press: Air pressure (Pa). Default is pressure at sea level (101325 Pa).
            reference_temp: Reference dry air temperature (C). Default is 0C,
                which is standard practice for SI enthalpy values. However, for
                IP enthalpy, this is typically at 0F (-17.78C). Alternatively, for
                aboslute thermodynamic enthalpy, one can input 0K (-273.15).

        Returns:
            Relative humidity (%).
        """
        return self._build_psychro_function(
            function=psychrometrics.rel_humid_from_db_enth,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'enthalpy': {
                    'input_type': 'Enthalpy',
                    'input_unit': 'kJ/kg'
                },
                'b_press': {
                    'input_type': 'Pressure',
                    'input_unit': 'Pa'
                },
                'reference_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                }
            },
            output_type='RelativeHumidity',
            output_unit='%',
            db_temp=db_temp,
            enthalpy=enthalpy,
            b_press=b_press,
            reference_temp=reference_temp,
        )

    def rel_humid_from_db_dpt(self, db_temp, dew_pt):
        """Relative humidity (%) from dry bulb temperature (C), and dew point temperature (C).

        Args:
            db_temp: Dry bulb temperature (C).
            dew_pt: Dew point temperature (C).

        Returns:
            Relative humidity (%).
        """
        return self._build_psychro_function(
            function=psychrometrics.dew_point_from_db_rh,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'dew_pt': {
                    'input_type': 'DewPointTemperature',
                    'input_unit': 'C'
                }
            },
            output_type='RelativeHumidity',
            output_unit='%',
            db_temp=db_temp,
            dew_pt=dew_pt,
        )

    def rel_humid_from_db_wb(self, db_temp, wet_bulb, b_press=101325):
        """Relative humidity (%) from dry bulb temperature (C), and wet bulb temperature (C).

        Args:
            db_temp: Dry bulb temperature (C).
            wet_bulb: Wet bulb temperature (C).
            b_press: Air pressure (Pa). Default is pressure at sea level (101325 Pa).

        Returns:
            Relative humidity (%).
        """
        return self._build_psychro_function(
            function=psychrometrics.rel_humid_from_db_wb,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'wet_bulb': {
                    'input_type': 'WetBulbTemperature',
                    'input_unit': 'C'
                },
                'b_press': {
                    'input_type': 'Pressure',
                    'input_unit': 'Pa'
                }
            },
            output_type='RelativeHumidity',
            output_unit='%',
            db_temp=db_temp,
            wet_bulb=wet_bulb,
            b_press=b_press,
        )

    def dew_point_from_db_hr(self, db_temp, humid_ratio, b_press=101325):
        """Dew Point Temperature (C) from air temperature (C) and humidity ratio (water/air).

        Args:
            db_temp: Dry bulb temperature (C).
            humid_ratio: Humidity ratio (kg water/kg air).
            b_press: Air pressure (Pa). Default is pressure at sea level (101325 Pa).

        Returns:
            Dew point temperature (C).
        """
        return self._build_psychro_function(
            function=psychrometrics.dew_point_from_db_hr,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'humid_ratio': {
                    'input_type': 'HumidityRatio',
                    'input_unit': '%'
                },
                'b_press': {
                    'input_type': 'Pressure',
                    'input_unit': 'Pa'
                }
            },
            output_type='DewPointTemperature',
            output_unit='C',
            db_temp=db_temp,
            humid_ratio=humid_ratio,
            b_press=b_press,
        )

    def dew_point_from_db_enth(self, db_temp, enthalpy, b_press=101325, reference_temp=0):
        """Dew point temperature (C) from air temperature (C) and enthalpy (kJ/kg).

        Args:
            db_temp: Dry bulb temperature (C).
            enthalpy: Enthalpy (kJ/kg).
            b_press: Air pressure (Pa). Default is pressure at sea level (101325 Pa).
            reference_temp: Reference dry air temperature (C). Default is 0C,
                which is standard practice for SI enthalpy values. However, for
                IP enthalpy, this is typically at 0F (-17.78C). Alternatively, for
                aboslute thermodynamic enthalpy, one can input 0K (-273.15).

        Returns:
            Dew point temperature (C).
        """
        return self._build_psychro_function(
            function=psychrometrics.dew_point_from_db_enth,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'enthalpy': {
                    'input_type': 'Enthalpy',
                    'input_unit': 'kJ/kg'
                },
                'b_press': {
                    'input_type': 'Pressure',
                    'input_unit': 'Pa'
                },
                'reference_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                }
            },
            output_type='DewPointTemperature',
            output_unit='C',
            db_temp=db_temp,
            enthlpy=enthalpy,
            b_press=b_press,
            reference_temp=reference_temp,
        )

    def dew_point_from_db_wb(self, db_temp, wet_bulb, b_press=101325):
        """Dew point temperature (C) from dry bulb (C) and wet bulb temperature (C).

        Args:
            db_temp: Dry bulb temperature (C).
            wet_bulb: Wet bulb temperature (C).
            b_press: Air pressure (Pa). Default is pressure at sea level (101325 Pa).

        Returns:
            Dew point temperature (C).
        """
        return self._build_psychro_function(
            function=psychrometrics.dew_point_from_db_wb,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'wet_bulb': {
                    'input_type': 'WetBulbTemperature',
                    'input_unit': 'C'
                },
                'b_press': {
                    'input_type': 'Pressure',
                    'input_unit': 'Pa'
                }
            },
            output_type='DewPointTemperature',
            output_unit='C',
            db_temp=db_temp,
            wet_bulb=wet_bulb,
            b_press=b_press,
        )

    def humid_ratio_from_db_wb(self, db_temp, wb_temp, b_press=101325):
        """Humidity ratio from air temperature (C) and wet bulb temperature (C).

        Args:
            db_temp: Dry bulb temperature (C).
            wb_temp: Wet bulb temperature (C).
            b_press: Air pressure (Pa). Default is pressure at sea level (101325 Pa).

        Returns:
            Humidity ratio (kg water / kg air).

        Note:
            [1] ASHRAE Handbook - Fundamentals (2017) ch. 1 eqn 36, solved for W
        """
        return self._build_psychro_function(
            function=psychrometrics.humid_ratio_from_db_wb,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'wb_temp': {
                    'input_type': 'WetBulbTemperature',
                    'input_unit': 'C'
                },
                'b_press': {
                    'input_type': 'Pressure',
                    'input_unit': 'Pa'
                }
            },
            output_type='HumidityRatio',
            output_unit='%',
            db_temp=db_temp,
            wb_temp=wb_temp,
            b_press=b_press,
        )

    def db_temp_from_enth_hr(self, enthalpy, humid_ratio, reference_temp=0):
        """Dry bulb temperature (C) from enthalpy (kJ/kg) and humidity ratio (water/air).

        Args:
            enthalpy: Enthalpy (kJ/kg).
            humid_ratio: Humidity ratio (kg water/kg air).
            reference_temp: Reference dry air temperature (C). Default is 0C,
                which is standard practice for SI enthalpy values. However, for
                IP enthalpy, this is typically at 0F (-17.78C). Alternatively, for
                aboslute thermodynamic enthalpy, one can input 0K (-273.15).

        Returns:
            Dry bulb temperature (C).

        Note:
            [1] ASHRAE Handbook - Fundamentals (2017) ch. 1 eqn 30
        """
        return self._build_psychro_function(
            function=psychrometrics.db_temp_from_enth_hr,
            input_kwargs={
                'enthalpy': {
                    'input_type': 'Enthalpy',
                    'input_unit': 'kJ/kg'
                },
                'humid_ratio': {
                    'input_type': 'HumidityRatio',
                    'input_unit': '%'
                },
                'reference_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                }
            },
            output_type='DryBulbTemperature',
            output_unit='C',
            enthalpy=enthalpy,
            humid_ratio=humid_ratio,
            reference_temp=reference_temp,
        )

    def dew_point_from_db_rh_fast(self, db_temp, rel_humid):
        """Dew point temperature (C) from air temperature (C) and relative humidity (%).

        Note that the formula here is fast but is only accurate up to 90C. For accurate
        values at extreme temperatures, the dew_point_from_db_rh
        function should be used.

        Args:
            db_temp: Dry bulb temperature (C).
            rel_humid: Relative humidity (%).

        Returns:
            Dew point temperature (C).

        Note:
            [1] J. Sullivan and L. D. Sanders. "Method for obtaining wet-bulb temperatures
            by modifying the psychrometric formula." Center for Experiment Design and Data
            Analysis. NOAA - National Oceanic and Atmospheric Administration.
            https://www.weather.gov/epz/wxcalc_rh
        """
        return self._build_psychro_function(
            function=psychrometrics.dew_point_from_db_rh_fast,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'rel_humid': {
                    'input_type': 'RelativeHumidity',
                    'input_unit': '%'
                },
            },
            output_type='DewPointTemperature',
            output_unit='C',
            db_temp=db_temp,
            rel_humid=rel_humid,
        )

    def wet_bulb_from_db_rh_fast(self, db_temp, rel_humid, b_press=101325):
        """Wet bulb temperature (C) from air temperature (C) and relative humidity (%).

        Note that the formula here is fast but is only accurate around temperatures
        of 20C and lower. For accurate values at extreme temperatures, the
        wet_bulb_from_db_rh function should be used.

        Args:
            db_temp: Dry bulb temperature (C).
            rel_humid: Relative humidity (%).
            b_press: Air pressure (Pa). Default is pressure at sea level (101325 Pa).

        Returns:
            Wet bulb temperature (C).

        Note:
            [1] J. Sullivan and L. D. Sanders. "Method for obtaining wet-bulb temperatures
            by modifying the psychrometric formula." Center for Experiment Design and Data
            Analysis. NOAA - National Oceanic and Atmospheric Administration.
            https://www.weather.gov/epz/wxcalc_rh
        """
        return self._build_psychro_function(
            function=psychrometrics.wet_bulb_from_db_rh_fast,
            input_kwargs={
                'db_temp': {
                    'input_type': 'DryBulbTemperature',
                    'input_unit': 'C'
                },
                'rel_humid': {
                    'input_type': 'RelativeHumidity',
                    'input_unit': '%'
                },
                'b_press': {
                    'input_type': 'Pressure',
                    'input_unit': 'Pa'
                }
            },
            output_type='WetBulbTemperature',
            output_unit='C',
            db_temp=db_temp,
            rel_humid=rel_humid,
            b_press=b_press,
        )

    def _d_ln_p_ws(self, db_temp):
        """Helper function returning the derivative of the natural log of the
        saturation vapor pressure as a function of dry-bulb temperature.

        Args:
            db_temp : Dry bulb temperature (C).
        Returns:
            Derivative of natural log of vapor pressure of saturated air in Pa.
        """
        return self._build_psychro_function(
            function=psychrometrics._d_ln_p_ws,
            input_kwargs={
                'db_temp': {
                    'input_type': 'WetBulbTemperature',
                    'input_unit': 'C'
                },
            },
            output_type='Pressure',
            output_unit='Pa',
            db_temp=db_temp,
            rel_humid=rel_humid,
            b_press=b_press,
        )
