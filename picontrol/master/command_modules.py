from picontrol import PiControlMessage_pb2 as PiControlMessage
from picontrol import PiNetworkCommand_pb2 as PiNetworkCommand
from picontrol import PiSystemCommand_pb2 as PiSystemCommand

import logging

logger = logging.getLogger(__name__)

_modules = {
    "systemCommand": PiSystemCommand,
    "networkCommand": PiNetworkCommand
}

def command_writer(func):
    def wrapper(*args, **kwargs):
        transport = args[0]._transport
        mod_name = args[0].module_name
        obj_name = func.__name__[0].lower() + func.__name__[1:]

        cmd_to_write = func(*args, **kwargs)
        msg = PiControlMessage.PiControlMessage()
        mod = getattr(msg.command, mod_name)
        cmd = getattr(mod, obj_name)
        copy = getattr(cmd, 'CopyFrom')
        copy(cmd_to_write)

        resp_data = transport.write_command(msg)
        protobuf_module = _modules[mod_name]
        cmd_obj = getattr(protobuf_module, func.__name__)
        resp = cmd_obj.Response()
        resp.ParseFromString(resp_data)
        return resp

    return wrapper

class SystemCommandModule(object):
    module_name = "systemCommand"

    def __init__(self, transport):
        self._transport = transport

    @command_writer
    def Shutdown(self):
        return PiSystemCommand.Shutdown()

    @command_writer
    def Reset(self):
        return PiSystemCommand.Reset()

class NetworkCommandModule(object):
    module_name = "networkCommand"

    def __init__(self, transport):
        self._transport = transport

    @command_writer
    def GetIPAddress(self, interface):
        cmd = PiNetworkCommand.GetIPAddress()
        cmd.interface = interface
        return cmd

    @command_writer
    def EnableInterface(self, interface, value):
        cmd = PiNetworkCommand.EnableInterface()
        cmd.interface = interface
        cmd.value = value
        return cmd

class CommandModules(object):
    def __init__(self, transport):
        self.system = SystemCommandModule(transport)
        self.network = NetworkCommandModule(transport)

def build_command_modules(transport):
    return CommandModules(transport)
