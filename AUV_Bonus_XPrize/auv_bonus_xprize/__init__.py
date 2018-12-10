import logging
from auv_bonus_xprize.settings import config

logging.basicConfig(filename=config['DEFAULT']['logfile'],
                    format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.DEBUG)
