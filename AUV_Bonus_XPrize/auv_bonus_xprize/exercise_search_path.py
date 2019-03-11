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
from auv_bonus_xprize.settings import config
from searchspace.searchspace import SearchSpace

ss = SearchSpace()

ss.set_search_boundaries()

ss.set_current_velocity()

search_path = ss.calculate_search_path()

for waypt in search_path:
    print(waypt)
