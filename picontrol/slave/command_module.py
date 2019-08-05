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

