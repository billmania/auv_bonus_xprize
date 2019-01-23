import pytest


def test_turn_toward_heading(monkeypatch, mocker):
    """test_turn_toward_heading()
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
    config['auv']['spiral_amount'] = '20'

    auv = Auv()

    assert auv.turn_toward_heading(90, 100) == 110
    assert auv.turn_toward_heading(100, 100) == 120
    assert auv.turn_toward_heading(100, 90) == 80
    assert auv.turn_toward_heading(350, 10) == 10
    assert auv.turn_toward_heading(10, 350) == 350
    assert auv.turn_toward_heading(90, 10) == 70
