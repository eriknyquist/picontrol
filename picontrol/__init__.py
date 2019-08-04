import sys
import os

script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_directory, 'protobuf/python'))

import PiControlMessage_pb2
import PiSystemCommand_pb2
import PiSystemEvent_pb2
import PiNetworkCommand_pb2
import PiNetworkEvent_pb2

import logging
logging.basicConfig()

