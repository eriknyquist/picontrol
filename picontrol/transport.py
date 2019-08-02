import struct
import binascii

from threading import Thread
from picontrol.event import Event

LENGTH_FIELD_SIZE = struct.calcsize('H')
HEADER_SIZE = struct.calcsize('HI')

class TransportLayer(object):
    def __init__(self, write_bytes_function, read_bytes_function):
        self._packet_received = Event()
        self._read_bytes = read_bytes_function
        self._write_bytes = write_bytes_function

        self._bytes = b''
        self._msg_size = None

        self._read_thread = Thread(target=self._read_task)
        self._read_thread.daemon = False
        self._read_thread.start()

    @property
    def on_packet_received(self):
        return self._packet_received

    def write_packet(self, message_data):
        length = len(message_data)
        crc = binascii.crc32(message_data)
        bytes_to_write = struct.pack('HI%ds'% length, length, crc, message_data)
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

            self._packet_received.generate(message_data)
            self._bytes = b''
            self._msg_size = None
