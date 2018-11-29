#!/usr/bin/python3
from pymoos import pymoos
import time


class UuvMOOS(pymoos.comms):
    """UuvMOOS is an example python MOOS app.
    It registers for 'NAV_HEADING'

    Attributes:
        moos_community: a string representing the address of the Community
        moos_port:      an interger defining the port
    """
    def __init__(self, moos_community, moos_port):
        """Initiates MOOSComms, sets the callbacks and runs the loop"""
        super(UuvMOOS, self).__init__()
        self.server = moos_community
        self.port = moos_port
        self.name = 'UuvMOOS'
        self.iter = 0
        self.fin_position = 5

        self.set_on_connect_callback(self._on_connect)
        self.set_on_mail_callback(self._on_new_mail)
        self.run(self.server, self.port, self.name)

    def _on_connect(self):
        """OnConnect callback"""
        print("Connected to", self.server, self.port,
              "under the name ", self.name)
        return self.register('NAV_HEADING', 0)

    def _on_new_mail(self):
        """OnNewMail callback"""
        for msg in self.fetch():
            if msg.key() == 'NAV_HEADING':
                self.iter += 1
                print('NAV_HEADING data: {0}, time: {1}'.format(
                    msg.double(), msg.time()
                ))
#                if (self.iter % 20) == 0:
#                    print('Moving the fins')
#                    self.fin_position = self.fin_position * -1
#                    self.notify('DESIRED_ELEVATOR',
#                                float(self.fin_position),
#                                -1
#                                )
#                    self.notify('DESIRED_THRUST',
#                                float(self.fin_position),
#                                -1
#                                )
        return True


def main():
    auv = UuvMOOS('localhost', 2345)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
