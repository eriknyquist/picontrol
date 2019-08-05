from picontrol.master.command_module import command_writer
from picontrol import PiSystemCommand_pb2 as PiSystemCommand

class SystemCommandModule(object):
    module_name = "systemCommand"
    protobuf_module = PiSystemCommand

    def __init__(self, transport):
        self._transport = transport

    @command_writer
    def Shutdown(self):
        return PiSystemCommand.Shutdown()

    @command_writer
    def Reset(self):
        return PiSystemCommand.Reset()

