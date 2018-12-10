def test_class_exists():
    from auv.auv import Auv
    auv = Auv()

    assert auv

def test_class_constructor():
    from auv.auv import Auv

    x_value = 1.1
    auv = Auv(x=x_value, y=2.2, depth=5.5)

    assert auv._current_pose['x'] == x_value

def test_class_constructor_args():
    from auv.auv import Auv

    x_value = 1.1
    auv = Auv(x=x_value, depth=5.5)

    assert auv._current_pose['y'] == 0.0

