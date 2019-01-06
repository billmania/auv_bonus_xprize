import pytest

def test_watchdog():
    """test_watchdog()
    """

    from time import time, sleep
    from auv_bonus_xprize.auv_main_loop import watchdog

    with pytest.raises(AttributeError):
        watchdog.reset_time is None

    watchdog()
    assert watchdog.reset_time == pytest.approx(time(), rel=0.0001)

    start_time = time()
    watchdog()
    sleep(1.0)
    watchdog()
    new_reset_time = start_time + 1.0
    assert watchdog.reset_time == pytest.approx(new_reset_time,
                                                rel=0.0001)
