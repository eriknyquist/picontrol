import sys
import os
import binascii

script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_directory, 'protobufs/python'))

import PiControlMessage_pb2 as PiControlMessage

def calculate_message_crc(message):
    message_copy = PiControlMessage.PiControlMessage()
    message_copy.CopyFrom(message)
    message_copy.crc = 0
    return binascii.crc32(message_copy.SerializeToString())

message = PiControlMessage.PiControlMessage()
message.command.networkCommand.getIPAddress.interface = "wlan123"
message.crc = calculate_message_crc(message)

print(message)

encoded = message.SerializeToString()

decoded = PiControlMessage.PiControlMessage()
decoded.ParseFromString(encoded)

calculated_crc = calculate_message_crc(decoded)
if calculated_crc != decoded.crc:
    raise ValueError("CRC mismatch! expected %d, got %d" % (calculated_crc, decoded.crc))

print(decoded)
