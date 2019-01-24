import pytest

@pytest.fixture()
def auv_position():
    auv_x = 100.0
    auv_y = 200.0
    auv_depth = 6.0

    return auv_x, auv_y, auv_depth

def test_new_search_area(monkeypatch, mocker, auv_position):
    """test_new_search_area()
    """

    from auv_bonus_xprize.auv_main_loop import new_search_area

    from auv.auv import variables_list

    def new_Auv_init(self):
        class new_Auv_MOOS(object):
            def publish_variable(self, variable, value, dummy):
                pass

        self._auv_data = dict()
        for variable_name in variables_list():
            self._auv_data[variable_name] = None

        self.auv_control = new_Auv_MOOS()

    from auv.auv import Auv
    monkeypatch.setattr(Auv,
                        '__init__',
                        new_Auv_init)

    from auv_bonus_xprize.settings import config

    easting_x = config['variables']['easting_x']
    northing_y = config['variables']['northing_y']
    depth = config['variables']['depth']
    auv = Auv()
    monkeypatch.setattr(auv,
                        '_auv_data',
                        {easting_x: auv_position[0],
                         northing_y: auv_position[1],
                         depth: auv_position[2]})

    config['starting']['set'] = '90'
    config['search']['min_depth_meters'] = '5.0'
    config['search']['up_current_offset'] = '5.0'
    config['search']['vertex_offset'] = '10.0'
    config['search']['min_depth_offset'] = '10.0'

    new_search_area(auv, object())
    assert config['starting']['auv_position_utm'] == '95.0,200.0'
    assert config['search']['min_depth_meters'] == '5.0'

    monkeypatch.setattr(auv,
                        '_auv_data',
                        {easting_x: auv_position[0],
                         northing_y: auv_position[1],
                         depth: 25.0})

    new_search_area(auv, object())
    assert config['search']['min_depth_meters'] == '15.0'
    assert config['starting']['northwest_utm'] == '85.0,210.0'
    assert config['starting']['northeast_utm'] == '105.0,210.0'
    assert config['starting']['southeast_utm'] == '105.0,190.0'
    assert config['starting']['southwest_utm'] == '85.0,190.0'
