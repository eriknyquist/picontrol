import logging

from picontrol.io.simple_tcp import SimpleTCPServer
from picontrol.slave.command_modules import build_command_modules
from picontrol.transport import TransportManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PiSlave(object):
    def __init__(self, write_bytes_function, read_bytes_function):
        self._transport = TransportManager(write_bytes_function, read_bytes_function,
                                           self._command_handler, None)

        self._command_modules = build_command_modules()

    def _command_handler(self, command):
        command_type = command.WhichOneof("commandModule")
        if command_type not in self._command_modules:
            logger.error("unhandled command type: %s" % command_type)
            return None

        logger.info("handling %s" % command_type)
        command_payload = getattr(command, command_type)
        command_module = self._command_modules[command_type]
        return command_module.handle_command(command_payload)


class PiTCPSlave(PiSlave):
    def __init__(self, ip, port):
        self._server = SimpleTCPServer(ip, port)
        self._server.start()
        super(PiTCPSlave, self).__init__(self._server.write_bytes,
                                         self._server.read_bytes)
