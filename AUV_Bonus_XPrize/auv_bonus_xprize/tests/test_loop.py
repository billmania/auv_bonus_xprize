import pytest

def test_set_loop_hz():
    """test_set_loop_hz()
    """

    from time import time
    from auv_bonus_xprize.auv_main_loop import set_loop_hz, loop_hz

    set_loop_hz(1.0)

    assert loop_hz.seconds_per_loop == 1.0
    assert loop_hz.start_time < time()
    assert not loop_hz.start_time > time()

def test_loop_hz():
    """test_loop_hz()
    """

    from time import time, sleep
    from auv_bonus_xprize.auv_main_loop import loop_hz

    seconds_per_loop = 2.0
    desired_hz = 0.5

    loop_hz.seconds_per_loop = seconds_per_loop
    loop_hz.start_time = time()

    start_time = loop_hz.start_time
    sleep(1.0)
    loop_hz()
    end_time = time()

    assert (end_time - start_time) == pytest.approx(seconds_per_loop,
                                                    rel=0.1)
    assert pytest.approx(loop_hz.start_time, rel=0.001) == (start_time + seconds_per_loop)

    start_time = loop_hz.start_time
    sleep(0.3)
    loop_hz()
    end_time = time()

    assert (end_time - start_time) == pytest.approx(seconds_per_loop,
                                                    rel=0.1)
    assert pytest.approx(loop_hz.start_time, rel=0.001) == (start_time + seconds_per_loop)

    start_time = loop_hz.start_time
    sleep(3.0)
    loop_hz()
    end_time = time()

    assert pytest.approx(loop_hz.start_time, rel=0.001) == end_time
