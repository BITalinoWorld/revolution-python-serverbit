"""
deviceFinder tools for SerberBIT 2018, adapted from PLUX openSignals module
wprimett@plux.info
# List PLUX device addresses and their types
# Enable OSC servers to find R-IoT modules
"""
"""
* Copyright (c) PLUX S.A., All Rights Reserved.
* (www.plux.info)
*
* This software is the proprietary information of PLUX S.A.
* Use is subject to license terms.
*
*
---------------------------------------------------------
.. module:: deviceFinder

.. moduleauthor:: pgoncalves <pgoncalves@plux.info


"""
import re
from riot_device_handler import *
riot_lib = riot_handler()

regex_bitalino = re.compile('[b|B][i|I][t|T][a|A][l|L][i|I][n|N][o|O]')
regex_bioplux = re.compile('[b|B][i|I][o|O][p|P][l|L][u|U][x|X]')
regex_biosignalsplux = re.compile('[b|B][i|I][o|O][s|S][i|I][g|G][n|N][a|A][l|L][s|S][p|P][l|L][u|U][x|X]')
regex_motionplux = re.compile('[m|M][o|O][t|T][i|I][o|O][n|N][p|P][l|L][u|U][x|X]')
regex_blebioplux = re.compile('[b|B][l|L][e|E][p|P][l|L][u|U][x|X]')
regex_gestureplux = re.compile('[g|G][e|E][s|S][t|T][u|U][r|R][e|E][p|P][l|L][u|U][x|X]')
regex_musclebanplux = re.compile('[m|M][u|U][s|S][c|C][l|L][e|E][b|B][a|A][n|N]')
regex_openbanplux = re.compile('[o|O][p|P][e|E][n|N][b|B][a|A][n|N][p|P][l|L][u|U][x|X]')
regex_riot = re.compile('/.*/raw')
regex_riot_bitalino = re.compile('/.*/bitalino')
regex_arduino = re.compile('usbmodem')

bluetooth_plist = "/Library/Preferences/com.apple.Bluetooth.plist"

def match_bitalino(str):
    return re.search(regex_bitalino, str) is not None


def match_bioplux(str):
    return re.search(regex_bioplux, str) is not None


def match_biosignalsplux(str):
    return re.search(regex_biosignalsplux, str) is not None


def match_motionplux(str):
    return re.search(regex_motionplux, str) is not None


def match_blebioplux(str):
    return re.search(regex_blebioplux, str) is not None


def match_gestureplux(str):
    return re.search(regex_gestureplux, str) is not None


def match_musclebanplux(str):
    return re.search(regex_musclebanplux, str) is not None


def match_openbanplux(str):
    return re.search(regex_openbanplux, str) is not None

def match_riot(str):
    return (re.search(regex_riot, str) is not None or re.search(regex_riot_bitalino, str) is not None)

def match_arduino(str):
    return (re.search(regex_arduino, str) is not None)

def is_plux_device(d):
    try:
        if check_type(d) == "arduino":
            return False
        return True
    except:
        return False

def check_type(str):
    if match_bitalino(str):
        return "bitalino"
    elif match_bioplux(str):
        return "bioplux"
    elif match_biosignalsplux(str):
        return "biosignalsplux"
    elif match_blebioplux(str):
        return "senseaid"
    elif match_motionplux(str):
        return "motionplux_champ"
    elif match_gestureplux(str):
        return "gestureplux"
    elif match_musclebanplux(str):
        return "musclebanplux"
    elif match_openbanplux(str):
        return "ddme_openbanplux"
    elif match_riot(str):
        return "R-Iot (OSC)"
    elif match_arduino(str):
        return "arduino"
    else:
        raise Exception("UNDEFINED_DEVICE_TYPE")


def findDevicesManually(device_type_connection, device_id, device_type):
    device_list = []
    device_name = str(device_id)
    device_connection = device_type_connection + device_name
    device_type = str(device_type)
    device_list.append([device_name, device_connection, device_type])
    return device_list

def findDevices(OS, enable_servers, riot_server_ready):
    starters = ['BLE', 'BTH']
    device_list = []
    # WINDOWS AND LINUX - SEARCH FOR NEARBY BLUETOOTH DEVICES
    if enable_servers["Bluetooth"]:
        if OS == 'windows' or OS == 'linux':
            from bluetooth import discover_devices, BluetoothError
            allDevices = []
            print ('searching for devices...')
            try:
                allDevices = discover_devices(duration=6, lookup_names=True)
                numDevices = len(allDevices)
                print ("found %i devices" % numDevices)
            except (BluetoothError, OSError) as e:
                print (e)
                print("+++++")
                print ("Please check bluetooth is turned on and try again")
                print("QUITAPP\n")
            for device in allDevices:
                try:
                    device_type = check_type(device[1])
                    device_list.append([device[0].upper(), device_type])
                except Exception as e:
                    pass
                    #print("DEVICE FINDER | " + str(mac) + ": " + str(e))
        # MACOS - LIST CURRENTLY PAIRED DEVICES
        else:
            print("listing PLUX devices")
            import biplist
            import binascii
            PersistentPorts = biplist.readPlist(bluetooth_plist)['PersistentPorts']
            for key, device in list(PersistentPorts.items()):
                print(key)
                print
                try:
                    device_connection = '/dev/tty.' + device['BTTTYName']
                    device_type = check_type(str(device_connection))
                    device_list.append([device_connection, device_type])
                except Exception as e:
                    pass
    ### OSC/riot devices
    if enable_servers["OSC"] and riot_server_ready:
        print("listing Riot devices")
        ip, port = enable_servers['OSC_config']['riot_ip'], enable_servers['OSC_config']['riot_port']
#        device_list.extend(riot_lib.fetch_devices(ip, port, 1))
        try:
            device_list.extend(riot_lib.fetch_devices(ip, port, 1))
        except Exception as e:
            print(e)
            pass
        print(device_list)
        # riot_handler.riot_handler()
    if enable_servers["Serial"]:
        import serial.tools.list_ports
        print("listing USB/Serial devices")
        ard_patt = re.compile('/dev/*.usbmodem')
        arduino_ports = [
            port.device for port in serial.tools.list_ports.comports()
            if re.match(ard_patt, port.device) or 'Arduino' in port.description
        ]
        for arduino_port in arduino_ports:
            try:
                device_list.append([arduino_port, 'arduino_usb'])
            except Exception as e:
                pass
    if enable_servers["UDP_out"]:
        import socket, time
        print("listing WiFi enabled arduino devices")

        UDP_IP = "0.0.0.0"
        UDP_PORT = 2390
        udp_listener = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP

        arduino_devices = []
        try:
            udp_listener.bind((UDP_IP, UDP_PORT))
            udp_listener.settimeout(5.0)
            data, addr = udp_listener.recvfrom(1024) # buffer size is 1024 bytes
            udp_listener.settimeout(None)
            print ("received message:", data.decode('utf-8'))
            print ("received message from:", addr)
            arduino_devices.append("%s-%s" % (data.decode('utf-8'), addr[0])) #include all responses
        except:
            pass
        arduino_devices = set(arduino_devices)
        for arduino_wifi_device in arduino_devices:
            try:
                device_list.append([arduino_wifi_device, 'arduino_wifi'])
            except Exception as e:
                pass

    return device_list
