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
import riot

regex_bitalino = re.compile('[b|B][i|I][t|T][a|A][l|L][i|I][n|N][o|O]')
regex_bioplux = re.compile('[b|B][i|I][o|O][p|P][l|L][u|U][x|X]')
regex_biosignalsplux = re.compile('[b|B][i|I][o|O][s|S][i|I][g|G][n|N][a|A][l|L][s|S][p|P][l|L][u|U][x|X]')
regex_motionplux = re.compile('[m|M][o|O][t|T][i|I][o|O][n|N][p|P][l|L][u|U][x|X]')
regex_blebioplux = re.compile('[b|B][l|L][e|E][p|P][l|L][u|U][x|X]')
regex_gestureplux = re.compile('[g|G][e|E][s|S][t|T][u|U][r|R][e|E][p|P][l|L][u|U][x|X]')
regex_musclebanplux = re.compile('[m|M][u|U][s|S][c|C][l|L][e|E][b|B][a|A][n|N]')
regex_openbanplux = re.compile('[o|O][p|P][e|E][n|N][b|B][a|A][n|N][p|P][l|L][u|U][x|X]')

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

def is_plux_device(d):
    try:
        check_type(d)
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
    else:
        raise Exception("UNDEFINED_DEVICE_TYPE")


def findDevicesManually(device_type_connection, device_id, device_type):
    device_list = []
    device_name = str(device_id)
    device_connection = device_type_connection + device_name
    device_type = str(device_type)
    device_list.append([device_name, device_connection, device_type])
    return device_list


def findDevices(OS, enable_servers):
    starters = ['BLE', 'BTH']
    device_list = []
    # WINDOWS AND LINUX - SEARCH FOR NEARBY BLUETOOTH DEVICES
    if OS == 'Windows' or OS == 'Linux':
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
        if enable_servers["Bluetooth"]:
            import biplist
            import binascii
            PersistentPorts = biplist.readPlist(bluetooth_plist)['PersistentPorts']
            for key, device in list(PersistentPorts.items()):
                try:
                    device_connection = '/dev/tty.' + device['BTTTYName']
                    device_type = check_type(str(device_connection))
                    device_list.append([device_connection, device_type])
                except Exception as e:
                    pass
        if enable_servers["OSC"]:
            device_list.extend(riot.fetch_devices(enable_servers['OSC_config'][0], enable_servers['OSC_config'][1], 1))
            print(device_list)

    return device_list
