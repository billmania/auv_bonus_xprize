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
"""AuvMOOS class
"""

from math import isnan
import logging
from pymoos import pymoos


class AuvMOOS(pymoos.comms):
    """AuvMOOS is the interface between the AUV control system
    and the MOOS subsystem .

    Attributes:
    """
    def __init__(self,
                 moos_community,
                 moos_port,
                 moos_name,
                 variables_list):
        """Initiates MOOSComms, sets the callbacks, registers the variables

        moos_community: a string representing the address of the Community
        moos_port:      the interger network port number
        moos_name:      how to identify this node
        variables_list: the list of variables to subscribe
        """

        super(AuvMOOS, self).__init__()
        self.community = moos_community
        self.port = moos_port
        self.name = moos_name
        self._variables_list = variables_list
        self._data_callback = None
        self.connected = False

        logging.debug('registering the on_connect callback')
        self.set_on_connect_callback(self._on_connect)
        logging.debug('registering the on_mail callback')
        self.set_on_mail_callback(self._on_new_mail)
        logging.debug('calling the pymoos.run() method')
        try:
            self.run(self.community, self.port, self.name)

        except Exception as e:
            logging.error('pymoos.run() excepted: {0}'.format(
                e))
            raise e

    def _on_connect(self):
        """_on_connect()

        wait_until_connected(self: pymoos.base_sync_comms, n_ms: int) -> bool
        is_connected(self: pymoos.base_sync_comms) -> bool
        """

        logging.info('Connected to MOOSDB at {0}:{1} named {2}'.format(
            self.community,
            self.port,
            self.name))

        try:
            self._register_variables()

            self.publish_variable('MOOS_MANUAL_OVERRIDE',
                                  'FALSE',
                                  -1)
            #
            # The next (misspelled) variable compensates for some
            # extremely sloppy MOOS code.
            #
            self.publish_variable('MOOS_MANUAL_OVERIDE',
                                  'FALSE',
                                  -1)

            self.publish_variable('RT_SET_ALT_PING_RATE',
                                  1,
                                  -1)
            self.publish_variable('RT_SET_ALT_TRIGGER',
                                  'auto',
                                  -1)
            self.connected = True

        except Exception as e:
            logging.error('Exception {0} in _on_connect()'.format(e))

    def _on_new_mail(self):
        """_on_new_mail()
        """

        for msg in self.fetch():
            if msg.key() in self._variables_list:
                if msg.is_double():
                    if isnan(msg.double()):
                        logging.warning('_on_new_mail(): {0} value is NaN'.format(msg.key()))
                        continue

                    variable_value = msg.double()
                elif msg.is_string():
                    variable_value = msg.string()
                elif msg.is_binary():
                    variable_value = msg.binary()
                else:
                    logging.warning(
                        'Variable {0} had unrecognized data type'.format(
                            msg.key()))
                    continue

                if self._data_callback:
                    try:
                        self._data_callback(msg.key(), variable_value)

                    except Exception as e:
                        logging.error('_on_new_mail() Exception: {0}'.format(
                            e))

        return True

    def _register_variables(self):
        """_register_variables()
        """
        for variable in self._variables_list:
            logging.debug('registering MOOS variable {0}'.format(variable))
            self.register(variable, 0)

    def publish_variable(self,
                         variable_name,
                         variable_value,
                         negative_one):
        """publish_variable()

        Publish the named variable with the provided value. The type of the
        value is expected to have been already set appropriately.
        """

        self.notify(variable_name, variable_value, negative_one)

    def set_data_callback(self, callback_function):
        """set_data_callback()

        Register a function to call with received MOOS variable data.
        """

        self._data_callback = callback_function
