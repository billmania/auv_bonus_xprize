#
# Designed and written by:
# Bill Mania
# bill@manialabs.us
#
# under contract to:
# Valley Christian Schools
# San Jose, CA
#
# to compete in the:
# NOAA Bonus XPrize
# January 2019
#
import logging
from auv_bonus_xprize.settings import config

logging.basicConfig(filename=config['DEFAULT']['logfile'],
                    format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.DEBUG)
