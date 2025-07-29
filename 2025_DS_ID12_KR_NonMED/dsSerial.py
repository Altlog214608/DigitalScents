""" Serial Thread """
from PySide6.QtCore import QThread
from PySide6.QtCore import QWaitCondition
from PySide6.QtCore import QMutex
from PySide6.QtCore import Signal # Slot
from PySide6.QtSerialPort import QSerialPortInfo

import serial

BAUDRATES = (9600, 19200, 38400, 57600, 115200)
DATABITS = (serial.FIVEBITS, serial.SIXBITS, serial.SEVENBITS, serial.EIGHTBITS)
FLOWCONTROL = ("No flowcontrol", "Hardware flowcontrol", "Software flowcontrol")
PARITY = (serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE)
STOPBITS = (serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO)

def _get_available_ports():
    return QSerialPortInfo().availablePorts()

def _is_open(_serial):
    if _serial and _serial.is_open:
        return True
    else:
        return False

def _open(_serial,
            port_name,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            flow_control="No flowcontrol",
            parity=serial.PARITY_NONE,
            stop_bits=serial.STOPBITS_ONE):
    """
    인자값으로 받은 시리얼 접속 정보를 이용하여 해당 포트를 연결
    :return: bool
    """
    print("dsSerial _open: ", port_name, baudrate)
    _serial.port = port_name
    _serial.baudrate = baudrate
    _serial.parity = parity
    _serial.stopbits = stop_bits
    _serial.bytesize = bytesize
    _serial.timeout = 0.05 # Read timeout 0: Non blocking (초 단위)
    _serial.write_timeout = 0 # Write timeout 0: Non blocking (초 단위)
    try:
        _serial.open()
    except Exception as err:
        print(err)
    return _serial.is_open

def _connect(_serial, _serial_read_thread,
             port_name, baudrate, bytesize, flow_control, parity, stop_bits):
    print("dsSerial _connect")
    serial_info = {
            "port_name": port_name,
            "baudrate": baudrate,
            "bytesize": bytesize,
            "flow_control": flow_control,
            "parity": parity,
            "stop_bits": stop_bits,
        }
    status = _open(_serial, **serial_info)
    _serial_read_thread.set_status(status)
    return status

def _connect_default(_serial, _serial_read_thread, 
                     port_name):
    print("dsSerial _connect_default")
    serial_info = {
            "port_name": port_name,  # "COM3",
            "baudrate": 9600,
            "bytesize": serial.EIGHTBITS,
            "flow_control": "No flowcontrol",
            "parity": serial.PARITY_NONE,
            "stop_bits": serial.STOPBITS_ONE,
        }
    status = _open(_serial, **serial_info)
    _serial_read_thread.set_status(status)
    return status

def _disconnect(_serial, _serial_read_thread):
    print("dsSerial _disconnect")
    _serial_read_thread.set_status(False)
    _serial.close()
    return False

class SerialReadThread(QThread):
    """SerialReadThread Class"""
    # 데이터 수신한 경우 Signal 전달
    _serial_received_data = Signal(bytes, name="serialReceivedData")

    def __init__(self, _serial):
        QThread.__init__(self)
        self.wait_condition = QWaitCondition()
        self.data_status = False
        self.mutex = QMutex()
        self._serial = _serial

    def __del__(self):
        self.wait()

    def run(self):
        # 들어온 데이터가 있다면 시그널을 발생
        while True:
            self.mutex.lock()
            if not self.data_status:
                self.wait_condition.wait(self.mutex)
            if self._serial and self._serial.is_open:
                buf = self._serial.readline()
                if buf:
                    # print("buf:", buf.hex())
                    self._serial_received_data.emit(buf)
            self.mutex.unlock()

    def toggle_status(self):
        print("dsSerial SerialReadThread toggle_status: ")
        self.data_status = not self.data_status
        if self.data_status:
            self.wait_condition.wakeAll()

    def set_status(self, status):
        print("dsSerial SerialReadThread set_status:", status)
        self.data_status = status
        if self.data_status:
            self.wait_condition.wakeAll()
