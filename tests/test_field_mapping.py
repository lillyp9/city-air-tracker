import pytest
from extract.daily_info import map_pollution_fields

#pulling the mapping
def test_map_air_pollution__history():

    fake_component = {
         'main': {'aqi': 2},
        'components': {
            'co': 137.02,
            'no': 0,
            'no2': 0.55,
            'o3': 18.06,
            'so2': 0.01,
            'pm2_5': 0.5,
            'pm10': 0.54,
            'nh3': 0.02
        }
    }

    result = map_pollution_fields(fake_component)

    assert result['aqi'] == 2
    assert result['carbon_monoxide'] == 137.02
    assert result['nitric_oxide'] == 0 
    assert result['nitrogen_dioxide'] == 0.55
    assert result['ozone'] == 18.06
    assert result['sulfur_dioxide'] == 0.01
    assert result['fine_particles'] == 0.5
    assert result['coarse_particles'] == 0.54
    assert result['ammonia'] == 0.02


def test_handles_zero_values_correctly():
    #zero is vaid reading , not missing data. This is to check it doenst get dropped or treated as null.
    fake_component = {
        'main': {'aqi':1},
        'components':{
            'co':0, 'no':0, 'no2':0, 'o3':0, 'so2':0, 'pm2_5':0, 'pm10':0, 'nh3':0
        }
    }

    result = map_pollution_fields(fake_component)

    assert result['carbon_monoxide'] == 0
    assert result['ozone'] == 0 


