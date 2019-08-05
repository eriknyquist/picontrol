from picontrol import PiControlMessage_pb2 as PiControlMessage
from picontrol import PiNetworkCommand_pb2 as PiNetworkCommand
from picontrol import PiSystemCommand_pb2 as PiSystemCommand

from picontrol.master.commands.system_command import SystemCommandModule
from picontrol.master.commands.network_command import NetworkCommandModule
import logging

logger = logging.getLogger(__name__)

class CommandModules(object):
    def __init__(self, transport):
        self.system = SystemCommandModule(transport)
        self.network = NetworkCommandModule(transport)

def build_command_modules(transport):
    return CommandModules(transport)
