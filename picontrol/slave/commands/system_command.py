from picontrol import PiSystemCommand_pb2 as PiSystemCommand
from picontrol.slave.command_module import CommandModule

class SystemCommandModule(CommandModule):
    module_name = "systemCommand"

    def __init__(self):
        super(SystemCommandModule, self).__init__(self.module_name)

    def shutdown(self, command):
        resp = PiSystemCommand.Shutdown.Response()
        resp.status = PiSystemCommand.OK
        return resp

    def reset(self, command):
        resp = PiSystemCommand.Reset.Response()
        resp.status = PiSystemCommand.OK
        return resp

