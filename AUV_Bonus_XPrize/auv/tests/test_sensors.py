import pytest


def test_altitude_ok(monkeypatch):
    """test_altitude_ok()
    """

    def new_Auv_init(self):
        class new_Auv_MOOS(object):
            def publish_variable(self, variable, value, dummy):
                pass

        self._auv_data = dict()
        self._auv_data['NAV_ALTITUDE'] = 5.0

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
    config['auv']['min_altitude_meters'] = '2.5'
    config['variables']['altitude'] = 'NAV_ALTITUDE'

    auv = Auv()

    assert auv.altitude_safety() == 0.0


def test_altitude_low(monkeypatch):
    """test_altitude_low()
    """

    def new_Auv_init(self):
        class new_Auv_MOOS(object):
            def publish_variable(self, variable, value, dummy):
                pass

        self._auv_data = dict()
        self._auv_data['NAV_ALTITUDE'] = 2.0

        self.auv_control = new_Auv_MOOS()

    from auv.auv import Auv
    monkeypatch.setattr(Auv,
                        '__init__',
                        new_Auv_init)

    from auv_bonus_xprize.settings import config
    config['auv']['min_altitude_meters'] = '2.5'
    config['variables']['altitude'] = 'NAV_ALTITUDE'

    auv = Auv()

    assert auv.altitude_safety() == 0.5
