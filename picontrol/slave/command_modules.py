from picontrol.slave.commands.system_command import SystemCommandModule
from picontrol.slave.commands.network_command import NetworkCommandModule

def build_command_modules():
    return {
        SystemCommandModule.module_name: SystemCommandModule(),
        NetworkCommandModule.module_name: NetworkCommandModule()
    }
