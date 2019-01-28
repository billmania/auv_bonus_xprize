from auv.watchdog import Watchdog

wd = Watchdog()

wd.stop()

print('Watchdog state')
if wd.watchdog_ready:
    print('Watchdog ready')
    if wd.watchdog_running:
        print('Watchdog counting down')
        print('Timer : {0}'.format(wd.watchdog_timer))
    else:
        print('Watchdog stopped')
else:
    print('Not ready')

print('Iridium status: {0}'.format(wd.iridium_status))
if wd.gps_fix:
    print('GPS has fix')
    print('GPS satellites: {0}'.format(wd.gps_satellites))
else:
    print('No GPS fix')
