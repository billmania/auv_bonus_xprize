import pytest


@pytest.fixture()
def auv_position():
    auv_x = 1.0
    auv_y = 2.0
    auv_depth = 5.0

    return auv_x, auv_y, auv_depth


@pytest.fixture()
def auv_waypoint(auv_position):
    waypoint_x = auv_position[0]
    waypoint_y = auv_position[1]
    waypoint_depth = auv_position[2]

    return waypoint_x, waypoint_y, waypoint_depth


def test_distance_to_waypoint(monkeypatch,
                              mocker,
                              auv_position,
                              auv_waypoint):
    """test_distance_to_waypoint()
    """

    from auv.auv import variables_list

    def new_Auv_init(self):
        class new_Auv_MOOS(object):
            def publish_variable(self, variable, value, dummy):
                pass

        self._auv_data = dict()
        for variable_name in variables_list():
            self._auv_data[variable_name] = None

        self._current_waypoint = dict()
        self._current_waypoint['x'] = 0.0
        self._current_waypoint['y'] = 0.0
        self._current_waypoint['depth'] = 0.0

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
                        {easting_x: auv_waypoint[0],
                         northing_y: auv_waypoint[1],
                         depth: auv_waypoint[2]})
    mocker.patch.object(auv, 'altitude_safety', return_value=0.0)

    auv._current_waypoint['x'] = auv_waypoint[0]
    auv._current_waypoint['y'] = auv_waypoint[1]
    auv._current_waypoint['depth'] = auv_waypoint[2]
    assert auv.distance_to_waypoint() == 0.0

    auv._current_waypoint['x'] = auv_waypoint[0]
    auv._current_waypoint['y'] = auv_waypoint[1] + 5.0
    auv._current_waypoint['depth'] = auv_waypoint[2]
    assert auv.distance_to_waypoint() == 5.0

    auv._current_waypoint['x'] = auv_waypoint[0]
    auv._current_waypoint['y'] = auv_waypoint[1]
    auv._current_waypoint['depth'] = auv_waypoint[2] + 5.0
    assert auv.distance_to_waypoint() == 0.0


def test_on_the_waypoint(monkeypatch, mocker):
    """test_on_the_waypoint()
    """

    from auv_bonus_xprize.settings import config
    config['auv']['distance_tolerance'] = '2.0'
    config['auv']['depth_tolerance'] = '1.0'
    config['variables']['easting_x'] = 'NAV_X'
    config['variables']['northing_y'] = 'NAV_Y'
    config['variables']['set_heading'] = 'DESIRED_HEADING'
    config['variables']['set_depth'] = 'DESIRED_DEPTH'
    config['variables']['set_speed'] = 'DESIRED_SPEED'
    config['variables']['depth'] = 'NAV_DEPTH'
    config['variables']['heading'] = 'NAV_HEADING'
    config['variables']['speed'] = 'NAV_SPEED'

    from auv.auv import variables_list

    def new_Auv_init(self):
        class new_Auv_MOOS(object):
            def publish_variable(self, variable, value, dummy):
                pass

        self._auv_data = dict()
        for variable_name in variables_list():
            self._auv_data[variable_name] = None

        self._current_waypoint = dict()
        self._current_waypoint['x'] = 0.0
        self._current_waypoint['y'] = 0.0
        self._current_waypoint['depth'] = 0.0

        self.auv_control = new_Auv_MOOS()

    from auv.auv import Auv
    monkeypatch.setattr(Auv,
                        '__init__',
                        new_Auv_init)

    auv = Auv()

    monkeypatch.setattr(auv,
                        '_auv_data',
                        {'NAV_X': 10.0,
                         'NAV_Y': 10.0,
                         'NAV_DEPTH': 5.0})
    mocker.patch.object(auv, 'altitude_safety', return_value=0.0)

    waypoint = (10, 10, 5, 90)
    assert auv.move_toward_waypoint(waypoint) == 'DONE'

    waypoint = (11, 10, 5, 90)
    assert auv.move_toward_waypoint(waypoint) == 'DONE'


def test_off_the_waypoint(monkeypatch, mocker):
    """test_off_the_waypoint()
    """

    from auv_bonus_xprize.settings import config
    config['auv']['distance_tolerance'] = '1.0'
    config['auv']['depth_tolerance'] = '1.0'
    config['variables']['easting_x'] = 'NAV_X'
    config['variables']['northing_y'] = 'NAV_Y'
    config['variables']['set_heading'] = 'DESIRED_HEADING'
    config['variables']['set_depth'] = 'DESIRED_DEPTH'
    config['variables']['set_speed'] = 'DESIRED_SPEED'
    config['variables']['depth'] = 'NAV_DEPTH'
    config['variables']['heading'] = 'NAV_HEADING'
    config['variables']['speed'] = 'NAV_SPEED'

    from auv.auv import variables_list

    def new_Auv_init(self):
        class new_Auv_MOOS(object):
            def publish_variable(self, variable, value, dummy):
                pass

        self._auv_data = dict()
        for variable_name in variables_list():
            self._auv_data[variable_name] = None

        self._current_waypoint = dict()
        self._current_waypoint['x'] = 0.0
        self._current_waypoint['y'] = 0.0
        self._current_waypoint['depth'] = 0.0

        self.auv_control = new_Auv_MOOS()

    from auv.auv import Auv
    monkeypatch.setattr(Auv,
                        '__init__',
                        new_Auv_init)

    auv = Auv()

    monkeypatch.setattr(auv,
                        '_auv_data',
                        {'NAV_X': 10.0,
                         'NAV_Y': 10.0,
                         'NAV_DEPTH': 5.0})
    mocker.patch.object(auv, 'altitude_safety', return_value=0.0)

    waypoint = (12, 10, 5, 90)
    assert auv.move_toward_waypoint(waypoint) == 'MORE'


def test_depth_is_off(monkeypatch, mocker):
    """test_on_the_waypoint()
    """

    from auv_bonus_xprize.settings import config
    config['auv']['distance_tolerance'] = '1.0'
    config['auv']['depth_tolerance'] = '1.0'
    config['variables']['easting_x'] = 'NAV_X'
    config['variables']['northing_y'] = 'NAV_Y'
    config['variables']['set_heading'] = 'DESIRED_HEADING'
    config['variables']['set_depth'] = 'DESIRED_DEPTH'
    config['variables']['set_speed'] = 'DESIRED_SPEED'
    config['variables']['depth'] = 'NAV_DEPTH'
    config['variables']['heading'] = 'NAV_HEADING'
    config['variables']['speed'] = 'NAV_SPEED'

    from auv.auv import variables_list

    def new_Auv_init(self):
        class new_Auv_MOOS(object):
            def publish_variable(self, variable, value, dummy):
                pass

        self._auv_data = dict()
        for variable_name in variables_list():
            self._auv_data[variable_name] = None

        self._current_waypoint = dict()
        self._current_waypoint['x'] = 0.0
        self._current_waypoint['y'] = 0.0
        self._current_waypoint['depth'] = 0.0

        self.auv_control = new_Auv_MOOS()

    from auv.auv import Auv
    monkeypatch.setattr(Auv,
                        '__init__',
                        new_Auv_init)

    auv = Auv()

    monkeypatch.setattr(auv,
                        '_auv_data',
                        {config['variables']['easting_x']: 10.0,
                         config['variables']['northing_y']: 10.0,
                         config['variables']['depth']: 3.0})
    mocker.patch.object(auv, 'altitude_safety', return_value=0.0)

    waypoint = (10, 10, 15, 90)
    assert auv.move_toward_waypoint(waypoint) == 'MORE'


def test_depth_is_close(monkeypatch, mocker):
    """test_on_the_waypoint()
    """

    from auv.auv import variables_list
    from auv_bonus_xprize.settings import config
    config['auv']['distance_tolerance'] = '1.0'
    config['auv']['depth_tolerance'] = '1.0'
    config['variables']['easting_x'] = 'NAV_X'
    config['variables']['northing_y'] = 'NAV_Y'
    config['variables']['set_heading'] = 'DESIRED_HEADING'
    config['variables']['set_depth'] = 'DESIRED_DEPTH'
    config['variables']['set_speed'] = 'DESIRED_SPEED'
    config['variables']['depth'] = 'NAV_DEPTH'
    config['variables']['heading'] = 'NAV_HEADING'
    config['variables']['speed'] = 'NAV_SPEED'

    def new_Auv_init(self):
        class new_Auv_MOOS(object):
            def publish_variable(self, variable, value, dummy):
                pass

        self._auv_data = dict()
        for variable_name in variables_list():
            self._auv_data[variable_name] = None

        self._current_waypoint = dict()
        self._current_waypoint['x'] = None
        self._current_waypoint['y'] = None
        self._current_waypoint['depth'] = None

        self.auv_control = new_Auv_MOOS()

    from auv.auv import Auv
    monkeypatch.setattr(Auv,
                        '__init__',
                        new_Auv_init)

    auv = Auv()

    monkeypatch.setattr(auv,
                        '_auv_data',
                        {'NAV_X': 10.0,
                         'NAV_Y': 10.0,
                         'NAV_DEPTH': 4.0})
    mocker.patch.object(auv, 'altitude_safety', return_value=0.0)

    waypoint = (10, 10, 5, 90)
    assert auv.move_toward_waypoint(waypoint) == 'DONE'
