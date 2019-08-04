import logging

from picontrol.io.simple_tcp import SimpleTCPClient
from picontrol.master.command_modules import build_command_modules
from picontrol.transport import TransportManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PiMaster(object):
    def __init__(self, write_bytes_function, read_bytes_function):
        self._transport = TransportManager(write_bytes_function, read_bytes_function,
                                           None, self._event_handler)

        self.commands = build_command_modules(self._transport)


class PiTCPMaster(PiMaster):
    def __init__(self, ip, port):
        self._client = SimpleTCPClient(ip, port)
        super(self, PiTCPMaster).__init__(self._client.write_bytes,
                                          self._client.read_bytes)
