import sys
import socket
import traceback
import logging
from threading import Thread, Event
from queue import Queue

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SimpleTCPServer(object):
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._sock = None
        self._conn = None
        self._connected = Event()
        self._client_thread = None
        self._main_thread = None
        self._input_queue = Queue()
        self._buffer = b''

    def start(self):
        if self._sock:
            return

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self._sock.bind((self._ip, self._port))
        except socket.error as msg:
            logger.error('bind failed. Error : ' + str(sys.exc_info()))
            sys.exit()

        self._main_thread = Thread(target=self._main_task)
        self._main_thread.daemon = False
        self._main_thread.start()

    def wait_for_connection(self, timeout=None):
        self._connected.wait(timeout)

    def write_bytes(self, bytes_to_write):
        if (not self._conn) or (not self._sock):
            raise ValueError("no client connected")

        self._conn.sendall(bytes_to_write)

    def read_bytes(self, num_bytes):
        if (not self._conn) or (not self._sock):
            raise ValueError("no client connected")

        ret = b''
        if len(self._buffer) > 0:
            ret = self._buffer[:num_bytes]
            self._buffer = self._buffer[num_bytes:]

        chunk = None
        remaining_bytes = num_bytes - len(ret)

        while remaining_bytes > 0:
            chunk = self._input_queue.get()
            slice_size = min(remaining_bytes, len(chunk))
            ret += chunk[:slice_size]
            chunk = chunk[slice_size:]
            remaining_bytes -= slice_size

        if chunk:
            self._buffer += chunk

        return ret

    def _main_task(self):
        self._sock.listen(10)
        logger.info('listening on %s:%d' % (self._ip, self._port))

        while True:
            self._conn, addr = self._sock.accept()
            self._connected.set()
            ip, port = str(addr[0]), str(addr[1])
            logger.info('accepting connection from ' + ip + ':' + port)

            try:
                self._client_thread = Thread(target=self._client_task,
                                             args=(ip, port))
                self._client_thread.daemon = False
                self._client_thread.start()
            except:
                traceback.print_exc()

        self._conn.close()
        self._sock = None


    def _client_task(self, ip, port, MAX_BUFFER_SIZE=4096):
        while True:
            try:
                received_bytes = self._conn.recv(MAX_BUFFER_SIZE)
            except:
                self._conn.close()
                print('connection ' + ip + ':' + port + " ended")
                self._connected.clear()
                traceback.print_exc()
                break

            size = sys.getsizeof(received_bytes)
            if  size >= MAX_BUFFER_SIZE:
                print("input length is probably too long: {}".format(size))

            self._input_queue.put(received_bytes)

class SimpleTCPClient(object):
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self._sock = None
        self._connected = Event()
        self._main_thread = None
        self._input_queue = Queue()
        self._buffer = b''
        self._start()

    def _start(self):
        if self._sock:
            return

        self._main_thread = Thread(target=self._main_task)
        self._main_thread.daemon = False
        self._main_thread.start()

    def wait_for_connection(self, timeout=None):
        self._connected.wait(timeout)

    def write_bytes(self, bytes_to_write):
        if (not self._connected.is_set()) or (not self._sock):
            raise ValueError("no client connected")

        self._sock.sendall(bytes_to_write)

    def read_bytes(self, num_bytes):
        if (not self._connected.is_set()) or (not self._sock):
            raise ValueError("no client connected")

        ret = b''
        if len(self._buffer) > 0:
            ret = self._buffer[:num_bytes]
            self._buffer = self._buffer[num_bytes:]

        chunk = None
        remaining_bytes = num_bytes - len(ret)
        while remaining_bytes > 0:
            chunk = self._input_queue.get()
            slice_size = min(remaining_bytes, len(chunk))
            ret += chunk[:slice_size]
            chunk = chunk[slice_size:]
            remaining_bytes -= slice_size

        self._buffer = chunk
        return ret

    def _main_task(self, MAX_BUFFER_SIZE=4096):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self._sock.connect((self._ip, self._port))
        except socket.error as msg:
            logger.error('connection failed. Error : ' + str(sys.exc_info()))
            sys.exit()

        self._connected.set()
        while True:
            try:
                received_bytes = self._sock.recv(MAX_BUFFER_SIZE)
            except:
                logger.error('connection ' + ip + ':' + port + " ended")
                self._connected.clear()
                traceback.print_exc()
                break

            size = sys.getsizeof(received_bytes)
            if  size >= MAX_BUFFER_SIZE:
                logger.error("input length is probably too long: {}".format(size))

            self._input_queue.put(received_bytes)

if __name__ == "__main__":
    #server = SimpleTCPServer("0.0.0.0", 11223)
    #server.start()
    #server.wait_for_connection()
    #while True:
    #    server.write_bytes(server.read_bytes(1))
    client = SimpleTCPClient("192.168.0.17", 11223)
    client.wait_for_connection()
    client.write_bytes(b'hello')
    print(client.read_bytes(4))
