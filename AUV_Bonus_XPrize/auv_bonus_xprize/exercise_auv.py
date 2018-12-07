from time import sleep

from auv_bonus_xprize.settings import config
from auv.auv import Auv


auv = Auv(x=float(config['starting']['latitude']),
          y=float(config['starting']['longitude']),
          depth=0.0,
          heading=int(config['starting']['heading']))

auv.auv_control._publish_variable('DESIRED_SPEED',
                                  50.0,
                                  -1)

sleep(1.0)

auv.auv_control._publish_variable('DESIRED_SPEED',
                                  0.0,
                                  -1)
