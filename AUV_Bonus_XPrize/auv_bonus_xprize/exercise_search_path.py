import pdb

from auv_bonus_xprize.settings import config
from searchspace.searchspace import SearchSpace

ss = SearchSpace(auv_latitude=30.0005,
                 auv_longitude=-10.0005)

ss.set_search_boundaries(northern_latitude=30.001,
                         southern_latitude=30.0,
                         eastern_longitude=-10.0,
                         western_longitude=-10.001,
                         depth=0.5)

ss.set_current_velocity(current_set=70,
                        current_drift=0)

pdb.set_trace()
search_path = ss.calculate_search_path()

for waypt in search_path:
    print(waypt)
