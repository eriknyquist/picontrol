import time

from queue import Queue

from picontrol import PiControlMessage_pb2 as PiControlMessage
from picontrol import PiNetworkCommand_pb2 as PiNetworkCommand
from picontrol.transport import TransportLayer, TransportManager

queue1 = Queue()
queue2 = Queue()

def write_to_queue1(message_data):
    for byte in message_data:
        queue1.put(byte)

def read_from_queue1(num_bytes):
    ret = b''
    for i in range(num_bytes):
        ret += bytes([queue1.get()])

    return ret

def write_to_queue2(message_data):
    for byte in message_data:
        queue2.put(byte)

def read_from_queue2(num_bytes):
    ret = b''
    for i in range(num_bytes):
        ret += bytes([queue2.get()])

    return ret

def command_handler(command):
    resp = PiNetworkCommand.GetIPAddress.Response()
    resp.address = "1.2.3.4"
    resp.status = PiNetworkCommand.OK
    return resp

sender = TransportManager(write_to_queue1, read_from_queue2)
receiver = TransportManager(write_to_queue2, read_from_queue1, command_handler)

message = PiControlMessage.PiControlMessage()
message.command.networkCommand.getIPAddress.interface = "wlan123"

print("sending message:")
print(message)

resp = sender.write_command(message)
print("got response:")
print(resp)
time.sleep(2)
