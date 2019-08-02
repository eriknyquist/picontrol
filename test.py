import sys
import os
import struct
import binascii
import time

from queue import Queue
from picontrol.transport import TransportLayer

script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_directory, 'protobuf/python'))

import PiControlMessage_pb2 as PiControlMessage

test_queue = Queue()

def write_to_queue(message_data):
    for byte in message_data:
        test_queue.put(byte)

def read_from_queue(num_bytes):
    ret = b''
    for i in range(num_bytes):
        ret += bytes([test_queue.get()])

    return ret

def packet_handler(message_data):
    msg = PiControlMessage.PiControlMessage()
    msg.ParseFromString(message_data)
    print("received message:")
    print(msg)

sender = TransportLayer(write_to_queue, None)
receiver = TransportLayer(write_to_queue, read_from_queue)
receiver.on_packet_received.add_handler(packet_handler)

message = PiControlMessage.PiControlMessage()
message.command.networkCommand.getIPAddress.interface = "wlan123"

print("sending message:")
print(message)

sender.write_packet(message.SerializeToString())
time.sleep(2)
