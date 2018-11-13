def test_move_to_waypoint_exists():
    from auv.auv import Auv
    auv = Auv()

    assert auv.move_to_waypoint

def test_distance_to_waypoint_exists():
    from auv.auv import Auv
    auv = Auv()

    assert auv.distance_to_waypoint

def test_distance_to_waypoint_exists():
    from auv.auv import Auv

    auv_x = 1.0
    auv_y = 2.0
    auv_depth = 5.0
    auv = Auv(x=auv_x, y=auv_y, depth=auv_depth)

    waypoint_x = auv_x
    waypoint_y = auv_y
    waypoint_depth = auv_depth
    auv._current_waypoint['x'] = waypoint_x
    auv._current_waypoint['y'] = waypoint_y
    auv._current_waypoint['depth'] = waypoint_depth

    assert auv.distance_to_waypoint() == 0.0

    waypoint_depth = auv_depth + 5.0
    auv._current_waypoint['depth'] = waypoint_depth

    assert auv.distance_to_waypoint() == 5.0
