import pytest
from auv_bonus_xprize.settings import config


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


def test_distance_to_waypoint(monkeypatch, auv_position, auv_waypoint):
    from auv.auv import Auv

    easting_x = config['variables']['easting_x']
    northing_y = config['variables']['northing_y']
    depth = config['variables']['depth']
    auv = Auv()
    monkeypatch.setattr(auv,
                        '_auv_data',
                        {easting_x: auv_waypoint[0],
                         northing_y: auv_waypoint[1],
                         depth: auv_waypoint[2]})

    auv._current_waypoint['x'] = auv_waypoint[0]
    auv._current_waypoint['y'] = auv_waypoint[1]
    auv._current_waypoint['depth'] = auv_waypoint[2]

    assert auv.distance_to_waypoint() == 0.0

    waypoint_depth = auv_position[2] + 5.0
    auv._current_waypoint['depth'] = waypoint_depth

    assert auv.distance_to_waypoint() == 5.0
