from time import sleep

from auv.auv import Auv

"""
from RiptideMicroUUVInterface.cpp

"""

auv = Auv()

while not auv.auv_control.connected:
    print('Waiting to connect')
    sleep(1.0)


iterations = 10
while iterations:
    auv.auv_control.publish_variable(
        'DESIRED_SPEED',
        0.05,
        -1)
    auv.auv_control.publish_variable(
        'DESIRED_HEADING',
        180.0,
        -1)
    auv.auv_control.publish_variable(
        'DESIRED_DEPTH',
        0.0,
        -1)
    sleep(1.0)

    iterations = iterations - 1

auv.auv_control.publish_variable(
    'DESIRED_SPEED',
    0.0,
    -1)

print('Done')
