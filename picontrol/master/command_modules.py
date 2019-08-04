from picontrol import PiNetworkCommand_pb2 as PiNetworkCommand
from picontrol import PiSystemCommand_pb2 as PiSystemCommand

class SystemCommandModule(object):
    module_name = "systemCommand"

    def __init__(self, transport):
        self._transport = transport
        super(self, SystemCommandModule).__init__(self.module_name)

    def Shutdown(self):
        cmd = PiSystemCommand.Shutdown()
        return self._transport.write_command(cmd)

    def Reset(self):
        cmd = PiSystemCommand.Reset()
        return self._transport.write_command(cmd)

class NetworkCommandModule(object):
    module_name = "networkCommand"

    def __init__(self, transport):
        self._transport = transport
        super(self, NetworkCommandModule).__init__(self.module_name)

    def GetIPAddress(self, interface):
        cmd = PiNetworkCommand.GetIPAddress()
        cmd.interface = interface
        return self._transport.write_command(cmd)

    def EnableInterface(self, interface, value):
        cmd = PiNetworkCommand.EnableInterface()
        cmd.interface = interface
        cmd.value = value
        return self._transport.write_command(cmd)

class CommandModules(object):
    def __init__(self, transport):
        self.system = SystemCommandModule(transport)
        self.network = NetworkCommandModule(transport)

def build_command_modules(transport):
    return CommandModules(transport)
