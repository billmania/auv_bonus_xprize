from time import sleep

from auv.auv import Auv

"""
from RiptideMicroUUVInterface.cpp

DESIRED_RUDDER integer degrees
DESIRED_ELEVATOR integer degrees
DESIRED_DEPTH
DESIRED_HEADING
DESIRED_SPEED

"""

speed_m_per_s = 0.5
speed_variable = 'DESIRED_SPEED'
base_angle = 10


def wiggle_controls():

    print('Wiggling')
    for angle in [-(base_angle), 0, base_angle]:
        print('Elevator: {0}'.format(angle))
        auv.auv_control.publish_variable('DESIRED_ELEVATOR',
                                          angle,
                                          -1)
        sleep(1.0)
    for angle in [-(base_angle), 0, base_angle]:
        print('Rudder: {0}'.format(angle))
        auv.auv_control.publish_variable('DESIRED_RUDDER',
                                          angle,
                                          -1)
        sleep(1.0)

auv = Auv()

while not auv.auv_control.connected:
    print('Waiting to connect')
    sleep(1.0)

print('Setting {0} to {1}'.format(speed_variable, speed_m_per_s))
while True:
    auv.auv_control.publish_variable(
        speed_variable,
        speed_m_per_s,
        -1)
    sleep(0.1)

sleep(5.0)

print('Done')
