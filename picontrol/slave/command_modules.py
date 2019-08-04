from picontrol import PiNetworkCommand_pb2 as PiNetworkCommand
from picontrol import PiSystemCommand_pb2 as PiSystemCommand

class CommandModule(object):
    def __init__(self, module_name):
        self._module_name = module_name

    def handle_command(self, command):
        command_type = command.WhichOneof("command")
        if not hasattr(self, command_type):
            raise RuntimeError("command module '%s' has no handler for command '%s'"
                               % (self._module_name, command_type))

        handler = getattr(self, command_type)
        command_payload = getattr(command, command_type)
        return handler(command_payload)

class SystemCommandModule(CommandModule):
    module_name = "systemCommand"

    def __init__(self):
        super(self, SystemCommandModule).__init__(self.module_name)

    def shutdown(self, command):
        resp = PiSystemCommand.Shutdown.Response()
        resp.status = PiSystemCommand.OK
        return resp

    def reset(self, command):
        resp = PiSystemCommand.Reset.Response()
        resp.status = PiSystemCommand.OK
        return resp

class NetworkCommandModule(CommandModule):
    module_name = "networkCommand"

    def __init__(self):
        super(self, NetworkCommandModule).__init__(self.module_name)

    def getIPAddress(self, command):
        resp = PiNetworkCommand.GetIPAddress.Response()
        resp.status = PiNetworkCommand.OK
        return resp

    def enableInterface(self, command):
        resp = PiNetworkCommand.EnableInterface.Response()
        resp.status = PiSystemCommand.OK
        return resp

def build_command_modules():
    return {
        SystemCommandModule.module_name: SystemCommandModule(),
        NetworkCommandModule.module_name: NetworkCommandModule()
    }
