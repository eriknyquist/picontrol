from picontrol import PiNetworkCommand_pb2 as PiNetworkCommand
from picontrol.slave.command_module import CommandModule

class NetworkCommandModule(CommandModule):
    module_name = "networkCommand"

    def __init__(self):
        super(NetworkCommandModule, self).__init__(self.module_name)

    def getIPAddress(self, command):
        resp = PiNetworkCommand.GetIPAddress.Response()
        resp.status = PiNetworkCommand.OK
        return resp

    def enableInterface(self, command):
        resp = PiNetworkCommand.EnableInterface.Response()
        resp.status = PiSystemCommand.OK
        return resp

