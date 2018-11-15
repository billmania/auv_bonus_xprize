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


@pytest.fixture()
def far_waypoint(auv_position):
    waypoint_x = auv_position[0] + 100.0
    waypoint_y = auv_position[1] + 100.0
    waypoint_depth = auv_position[2] + 500.0

    return waypoint_x, waypoint_y, waypoint_depth


def test_distance_to_waypoint(auv_position, auv_waypoint):
    from auv.auv import Auv

    auv = Auv(x=auv_position[0], y=auv_position[1], depth=auv_position[2])

    auv._current_waypoint['x'] = auv_waypoint[0]
    auv._current_waypoint['y'] = auv_waypoint[1]
    auv._current_waypoint['depth'] = auv_waypoint[2]

    assert auv.distance_to_waypoint() == 0.0

    waypoint_depth = auv_position[2] + 5.0
    auv._current_waypoint['depth'] = waypoint_depth

    assert auv.distance_to_waypoint() == 5.0


def test_record_pose_update(auv_position):
    from auv.auv import Auv

    nav_x = 2.3
    nav_y = 3.1
    nav_depth = 12.0
    nav_heading = 45

    auv = Auv(x=auv_position[0], y=auv_position[1], depth=auv_position[2])
    auv.record_pose_update(
        x=nav_x,
        y=nav_y,
        depth=nav_depth,
        heading=nav_heading)

    assert auv._current_pose['x'] == nav_x
    assert auv._current_pose['y'] == nav_y
    assert auv._current_pose['depth'] == nav_depth
    assert auv._current_pose['heading'] == nav_heading

def test_settings_for_waypoint(auv_position, auv_waypoint):
    from auv.auv import Auv

    auv = Auv(x=auv_position[0], y=auv_position[1], depth=auv_position[2])

    prop, elevator, rudder = auv.settings_for_waypoint(auv_waypoint)
    assert prop == 0.0
    assert elevator == 0.0
    assert rudder == 0.0

    prop, elevator, rudder = auv.settings_for_waypoint(far_waypoint)
    assert prop == float(config['auv']['max_prop_speed'])
    assert elevator == -float(config['auv']['max_elevator'])
    assert rudder != 0.0
