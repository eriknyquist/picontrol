from picontrol.master.command_module import command_writer
from picontrol import PiNetworkCommand_pb2 as PiNetworkCommand

class NetworkCommandModule(object):
    module_name = "networkCommand"
    protobuf_module = PiNetworkCommand

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
