"""Watchdog

The functionality for the Iridium module as a watchdog.
"""

import logging
from time import sleep
from serial import Serial, SerialException, SerialTimeoutException
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from auv_bonus_xprize.settings import config

START = '$'
END = '\n'
SUCCESS = 'SUCCESS'
FAILURE = 'FAIL'
RESET = 'WDTRESET'
STOP = 'WDTSTOP'
SEND = 'SBD,'
STATUS = 'STATUS'
MAX_MSG_LENGTH = 120


class Watchdog(object):
    """Watchdog - The watchdog module

    """

    def __init__(self):
        """__init__() - Create an instance of the Watchdog
        """

        try:
            self._wd = Serial(
                port=config['watchdog']['port'],
                baudrate=int(config['watchdog']['data_rate']),
                bytesize=EIGHTBITS,
                parity=PARITY_NONE,
                stopbits=STOPBITS_ONE,
                timeout=1)
            self._wd.rts = True
            self._wd.dtr = True
            self._wd.reset_input_buffer()
            self._wd.reset_output_buffer()

            self.watchdog_ready = True
            self.iridium_status = None
            self.gps_satellites = None
            self.gps_fix = False
            self.watchdog_running = False
            self.watchdog_timer = None

            sleep(1.0)

            self.status()

        except SerialException as e:
            msg = 'Exception opening watchdog port {0}: {1}'.format(
                config['watchdog']['port'],
                e)
            logging.warning(msg)
            self.watchdog_ready = False

    def reset(self):
        """reset()

        Reset the watchdog timer.
        """

        self._write_msg(RESET)
        self.status()
        if not self.watchdog_running:
            logging.error('Failed to reset the watchdog')

    def stop(self):
        """stop()

        Stop the watchdog from running.
        """

        self._write_msg(STOP)
        self.status()
        if not self.watchdog_running:
            logging.info('Watchdog timer stopped')
        else:
            logging.error('Failed to stop the watchdog')

    def send(self, msg_text):
        """send()

        Send a message.
        """

        msg = SEND + msg_text[:MAX_MSG_LENGTH]
        self._write_msg(msg)

        result = list()
        iterations = 20
        while not result and iterations:
            iterations = iterations - 1

            self.reset()
            sleep(30.0)
            result = self._read_msg()

        if result and result[0] == SUCCESS:
            return True
        else:
            logging.warning('Failed to send message: {0}'.format(
                msg))
            return False

    def status(self):
        """status()

        Get the status of the watchdog system.
        """

        self._write_msg(STATUS)

        result = self._read_msg()
        if result and result[0] == STATUS:
            self.iridium_status = int(result[1])
            self.gps_satellites = int(result[2])
            self.gps_fix = int(result[3]) == 1
            self.watchdog_running = int(result[4]) == 1
            self.watchdog_timer = int(result[5])

        else:
            logging.warning('Failed to get watchdog status')

            self.iridium_status = 0
            self.gps_satellites = 0
            self.gps_fix = False
            self.watchdog_running = True
            self.watchdog_timer = None

    def _read_msg(self):
        """_read_msg()

        Read a watchdog message from the serial port, extracting
        the message type and stripping the prefix and suffix.
        """

        try:
            raw_msg = self._wd.read_until()
            msg = raw_msg.decode("utf-8")
            if not msg:
                return list()

            if msg[0] == START and msg[-1:] == END:
                return msg[1:-1].split(',')

        except SerialTimeoutException:
            pass

        except Exception as e:
            logging.error('Exception with msg {0}: {1} - {2}'.format(
                msg,
                len(msg),
                e))

        return list()

    def _write_msg(self, msg_body):
        """_write_msg()

        Build a complete message from msg_body and write it to
        the serial port.
        """

        msg = START + msg_body + END
        try:
            self._wd.write(msg.encode('utf-8'))
            self._wd.flush()

        except SerialTimeoutException:
            log_msg = 'Failed to write watchdog message: {0}'.format(
                msg_body)
            logging.warning(log_msg)
