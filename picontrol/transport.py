import struct
import binascii
import threading
import logging

from picontrol.event import Event
import PiControlMessage_pb2 as PiControlMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

LENGTH_FIELD_SIZE = struct.calcsize('H')
HEADER_SIZE = struct.calcsize('HI')
COMMAND_TIMEOUT_SEC = 10

class TransportLayer(object):
    def __init__(self, write_bytes_function, read_bytes_function, packet_handler):
        self._packet_handler = packet_handler
        self._read_bytes = read_bytes_function
        self._write_bytes = write_bytes_function

        self._bytes = b''
        self._msg_size = None

        self._read_thread = threading.Thread(target=self._read_task)
        self._read_thread.daemon = False
        self._read_thread.start()

    def write_packet(self, message_data):
        length = len(message_data)
        crc = binascii.crc32(message_data)
        bytes_to_write = struct.pack('HI%ds'% length, length, crc, message_data)

        logger.info('writing packet: %s' % bytes_to_write.hex())
        self._write_bytes(bytes_to_write)

    def _read_task(self):
        if not self._read_bytes:
            return

        while True:
            self._byte_received(self._read_bytes(1))

    def _byte_received(self, byte):
        self._bytes += byte
        num_bytes = len(self._bytes)

        if num_bytes == LENGTH_FIELD_SIZE:
            self._msg_size = struct.unpack('H', self._bytes)[0]
        elif self._msg_size and (num_bytes == (self._msg_size + HEADER_SIZE)):
            _, crc, message_data = struct.unpack('HI%ds' % self._msg_size,
                                                 self._bytes)

            calculated_crc = binascii.crc32(message_data)
            if calculated_crc != crc:
                raise RuntimeError("CRC mismatch! expected %d, got %d" %
                                   (calculated_crc, crc))

            logger.info('received packet: %s' % self._bytes.hex())

            if self._packet_handler:
                self._packet_handler(message_data)

            self._bytes = b''
            self._msg_size = None

class TransportManager(object):
    def __init__(self, write_bytes_function, read_bytes_function,
                 command_handler=None, event_handler=None):
        self._handled_command = threading.Event()
        self._handled_command.set()

        self._response_received = threading.Event()
        self._response_received.set()
        self._response_data = None

        self._command_handler = command_handler
        self._event_handler = event_handler
        self._transport = TransportLayer(write_bytes_function,
                                         read_bytes_function,
                                         self._packet_handler)

    def _packet_handler(self, message_data):
        msg = PiControlMessage.PiControlMessage()
        msg.ParseFromString(message_data)
        message_type = msg.WhichOneof("messageData")
        if message_type == "command":
            if self._command_handler is None:
                return

            self._handled_command.clear()
            response_payload = self._command_handler(msg.command)
            response = PiControlMessage.PiControlMessage()
            response.response.responseData = response_payload.SerializeToString()
            self._write_message(response)
            self._handled_command.set()
        elif message_type == "response":
            if self._response_received.is_set():
                logger.error("unexpected response received!")
            else:
                self._response_data = msg.response.responseData
                self._response_received.set()

        elif message_type == "event":
            if self._event_handler is None:
                return

            self._event_handler(msg.event)
        else:
            logger.error("unhandled message type '%s'" % message_type)

    def _write_message(self, message):
        self._transport.write_packet(message.SerializeToString())

    def write_event(self, event):
        # If we are currently handling a command, wait for that to finish
        handled = self._handled_command.wait(COMMAND_TIMEOUT_SEC)
        if not handled:
            raise RuntimeError("Timed out waiting for command to be handled")

        # Write out event data
        self._write_message(event)

    def write_command(self, command):
        # If we are currently handling a command, wait for that to finish
        handled = self._handled_command.wait(COMMAND_TIMEOUT_SEC)
        if not handled:
            raise RuntimeError("Timed out waiting for command to be handled")

        # Send command data
        self._response_received.clear()
        self._write_message(command)

        # Wait for response to be received
        received = self._response_received.wait(COMMAND_TIMEOUT_SEC)

        # Ensure response flag is reset
        self._response_received.set()

        if not received:
            raise RuntimeError("Command timed out: no response received")

        return self._response_data
