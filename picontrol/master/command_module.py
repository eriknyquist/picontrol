from picontrol import PiControlMessage_pb2 as PiControlMessage

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
        cmd_obj = getattr(args[0].protobuf_module, func.__name__)
        resp = cmd_obj.Response()
        resp.ParseFromString(resp_data)
        return resp

    return wrapper

