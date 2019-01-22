"""DyeSensor

The functionality for the Turner Cyclops 7F dye sensor.
"""

import logging
from Adafruit_ADS1x15 import ADS1115
from auv_bonus_xprize.settings import config

ADC_GAIN = 1


class DyeSensor(object):
    """DyeSensor - The Turner Cyclops 7F class.

    """

    def __init__(self):
        """__init__() - Create an instance of the DyeSensor
        """

        try:
            self.sensor = ADS1115()

        except Exception as e:
            logging.error('Exception in DyeSensor: {0}'.format(
                e))
            self.sensor = None

    def no_gain(self):
        """no_gain()

        Set the sensor gain to zero.
        """

        pass

    def ten_gain(self):
        """ten_gain()

        Set the sensor gain to 10x.
        """

        pass

    def hundred_gain(self):
        """hundred_gain()

        Set the sensor gain to 100x.
        """

        pass

    def sensor_value(self):
        """sensor_value()

        Return the current reading from the sensor,
        at the current gain.
        """

        sensor_value = self.sensor.read_adc(0, gain=ADC_GAIN)

        if sensor_value < int(config['dye_sensor']['min_sensor_value']):
            logging.debug('dye sensor under threshold: {0}'.format(
                sensor_value))
            return 0
        else:
            return sensor_value
