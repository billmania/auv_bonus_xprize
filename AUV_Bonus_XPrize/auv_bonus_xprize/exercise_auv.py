from time import sleep

from auv_bonus_xprize.settings import config
from auv.auv import Auv

"""
DESIRED_RUDDER integer degrees
DESIRED_ELEVATOR integer degrees
DESIRED_DEPTH
DESIRED_HEADING
DESIRED_SPEED
RT_THRUST_SPEED integer 0 to 3-ish
"""

thrust = 3
base_angle = 10

def wiggle_controls():

    print('Wiggling')
    for angle in [-(base_angle), 0, base_angle]:
        print('Elevator: {0}'.format(angle))
        auv.auv_control._publish_variable('DESIRED_ELEVATOR',
                                          angle,
                                          -1)
        sleep(1.0)
    for angle in [-(base_angle), 0, base_angle]:
        print('Rudder: {0}'.format(angle))
        auv.auv_control._publish_variable('DESIRED_RUDDER',
                                          angle,
                                          -1)
        sleep(1.0)

auv = Auv(x=float(config['starting']['latitude']),
          y=float(config['starting']['longitude']),
          depth=0.0,
          heading=int(config['starting']['heading']))

while not auv.auv_control.connected:
    print('Waiting to connect')
    sleep(1.0)

wiggle_controls()

print('Centering controls')
auv.auv_control._publish_variable('DESIRED_ELEVATOR',
                                  0,
                                  -1)
auv.auv_control._publish_variable('DESIRED_RUDDER',
                                  0,
                                  -1)

print('Setting thrust to {0}'.format(thrust))
auv.auv_control._publish_variable('RT_THRUST_SPEED',
                                  thrust,
                                  -1)
sleep(1.0)

print('Stopped')
auv.auv_control._publish_variable('RT_THRUST_SPEED',
                                  0,
                                  -1)
print('Done')