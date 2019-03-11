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
import sys
from configparser import ConfigParser

config = ConfigParser()
CONFIG_FILE = '/usr/local/etc/auv_bonus_xprize.config'

try:
    config.read_file(open(CONFIG_FILE))

except FileNotFoundError as e:
    print('Failed to find and read config file {0}'.format(
        CONFIG_FILE))

    sys.exit(1)
