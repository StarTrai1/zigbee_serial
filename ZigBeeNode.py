import serial
import platform
import time
import serial.tools.list_ports
import sys
'''

'''
class ZigBeeNode(object):
    
    ###
    #   hex commands set
    #   cmd : commands (string format, need to convert to hex format)
    #   rlen: read rlen bytes
    ###
    hex_cmds = {
        'dev_type'        : {"cmd": 'fe 01 01 ff', 'rlen': 2},
        'nwk_state'       : {"cmd": 'fe 01 02 ff', 'rlen': 2},
        'pan_id'          : {"cmd": 'fe 01 03 ff', 'rlen': 3},
        'key'             : {"cmd": 'fe 01 04 ff', 'rlen': 17},
        'shortAddr'       : {"cmd": 'fe 01 05 ff', 'rlen': 3},
        'macAddr'         : {"cmd": 'fe 01 06 ff', 'rlen': 9},
        'coor_shortAddr'  : {"cmd": 'fe 01 07 ff', 'rlen': 3},
        'coor_macAddr'    : {"cmd": 'fe 01 08 ff', 'rlen': 9},
        'group_id'        : {"cmd": 'fe 01 09 ff', 'rlen': 2},
        'channel'         : {"cmd": 'fe 01 0a ff', 'rlen': 2},
        'txpower'         : {"cmd": 'fe 01 0b ff', 'rlen': 2},
        'baud_rate'       : {"cmd": 'fe 01 0c ff', 'rlen': 2},
        'sleep_time'      : {"cmd": 'fe 01 0d ff', 'rlen': 2},
        'save_time'       : {"cmd": 'fe 01 0e ff', 'rlen': 2},
        'all_info'        : {"cmd": 'fe 01 fe ff', 'rlen': 45},
    }

    BAUDRATES = (2400, 4800, 9600, 14400, 19200, 38400, 43000, 57600, 76800, 115200, 128000)

    # device typs
    dev_types = {"00": "Coordinator", "01": "Router", "02": "End Device"}

    default_baudrate = 115200

    def _init_serial(self):
        pltfm = platform.system()
        port_type = "USB"
        serialName = None
        serial_port = None
        if pltfm == "Linux":
            print("future work")
        elif pltfm == "Windows":
            for port in serial.tools.list_ports.comports():
                # find USB serial
                if port[1].find(port_type)!=-1:
                    try:
                        serialName = port[0]
                        serial_port = serial.Serial(port=serialName, baudrate=self.default_baudrate, timeout = 1)
                    except serial.serialutil.SerialException as e:
                        # this serial is opened by other program
                        if e.args[0].find("PermissionError") != -1:
                            continue
                        else:
                            break
                    except Exception as e:
                        print(e)
                        break
                    if serial_port.isOpen() == True:
                        print("open {} successfully".format(serialName))
                        break
        return serial_port

    def sendHexCmd(self, cmd):
        return self.serial_port.write(bytes.fromhex(cmd))

    def readHexCmdResult(self, length):
        return self.serial_port.read(length)

    def _get_zigbee_info(self):
        self.sendHexCmd(self.hex_cmds['all_info']['cmd'])
        result = self.readHexCmdResult(self.hex_cmds['all_info']['rlen'])
        if result[0:1] == b'\xfb':
            return result[1:]
        return "get failed"

    def print_all_info(self):
        print('dev_type: {}'.format(self.dev_types[bytes.hex(self.dev_type)]))
        print('nwk_state: {}'.format(bytes.hex(self.nwk_state)))
        print('pan_id: {}'.format(bytes.hex(self.pan_id)))
        print('key: {}'.format(bytes.hex(self.key)))
        print('shortAddr: {}'.format(bytes.hex(self.shortAddr)))
        print('macAddr: {}'.format(bytes.hex(self.macAddr)))
        print('coor_shortAddr: {}'.format(bytes.hex(self.coor_shortAddr)))
        print('coor_macAddr: {}'.format(bytes.hex(self.coor_macAddr)))
        print('group_id: {}'.format(bytes.hex(self.group_id)))
        print('channel: {}'.format(bytes.hex(self.channel)))
        print('txpower: {}'.format(bytes.hex(self.txpower)))
        print('baud_rate: {}'.format(bytes.hex(self.baudrate)))
        print('sleep_time: {}'.format(bytes.hex(self.sleep_time)))

    def print_dev_type(self):
        print('dev_type: {}'.format(self.dev_types[bytes.hex(self.dev_type)]))

    def print_coor_shortAddr(self):
        print('dev_type: {}'.format(self.dev_types[bytes.hex(self.dev_type)]))

    def __init__(self):
        self.serial_port = self._init_serial()
        if self.serial_port is None:
            print("No ports or ports are occupied!")
            sys.exit(0)
        print("begin to initialize")
        counter = 0
        while True:
            self.all_info = self._get_zigbee_info()
            if self.all_info != 'get failed':
                break
            else:
                print("Waiting for the node to initialize")
                time.sleep(0.1)
            if counter >=10:
                print("timeout")
                sys.exit(0)
            counter+=1
        self.dev_type = self.all_info[0:1]
        print('dev_type: {}'.format(self.dev_types[bytes.hex(self.dev_type)]))
        self.nwk_state = self.all_info[1:2]
        self.pan_id = self.all_info[2:4]
        self.key = self.all_info[4: 20]
        self.shortAddr = self.all_info[20: 22]
        self.macAddr = self.all_info[22:30]
        self.coor_shortAddr = self.all_info[30:32]
        self.coor_macAddr = self.all_info[32: 40]
        self.group_id = self.all_info[40:41]
        self.channel = self.all_info[41:42]
        self.txpower = self.all_info[42:43]
        self.baudrate = self.all_info[43:44]
        self.sleep_time = self.all_info[44:45]

    def hex_broadcastSend(self, data, send_mode):
        if send_mode == "01":
            print("only suit to all nodes on node 3 or coordinator on mode 2")
            return

        data = self.data2hexstr(data)
        data_length = len(data)//2
        if data_length > 255:
            print("data length is over 255 bytes")
            return
        elif data_length//10 == 0:
            data_length = "0"+str(data_length+2)

        cmd = 'fc{}01{}{}'.format(data_length, send_mode, data)
        return self.sendHexCmd(cmd)

    def hex_groupSend(self, data, group_id):

        if group_id<0 or group_id >99:
            print("group_id is out of range")
            return
        group_id = '0'+str(group_id) if group_id//10==0 else str(group_id)
        data = self.data2hexstr(data)
        data_length = len(data)//2
        if data_length > 255:
            print("data length is over 255 bytes")
            return
        elif data_length//10 == 0:
            data_length = "0"+str(data_length+2)
        print(data_length)
        cmd = 'fc{}02{}{}'.format(data_length, group_id, data)
        print(cmd)
        return self.sendHexCmd(cmd)

    def hex_p2pSend(self, data, addr, mode):

        if 0xfff8<int(addr, 16) or int(addr, 16)<0x0000:
            print("invalid address")
            return

        data = self.data2hexstr(data)
        data_length = len(data)//2
        if data_length > 255:
            print("data length is over 255 bytes")
            return
        elif data_length//10 == 0:
            data_length = "0"+str(data_length+4)

        cmd = 'fc{}03{}{}{}'.format(data_length, mode, addr, data)
        print(cmd)
        return self.sendHexCmd(cmd)

    def hex_receive(self, size=1):
        return self.serial_port.read(size=size)

    def finish(self):
        self.serial_port.close()

    def data2hexstr(self, data, encoding="utf8"):
        return bytes(data, encoding=encoding).hex()
