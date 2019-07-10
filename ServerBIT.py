import importlib
from importlib import import_module
from tornado import websocket, web, ioloop # used for html config page
# import _thread as thread
import threading
import websockets # used for real-time data streaming
import asyncio
import json, signal, numpy
import sys, traceback, os, time
from os.path import expanduser
import fileinput, time
from shutil import copyfile, rmtree
import subprocess

import deviceFinder as deviceFinder
from bitalino import *
from ServerOSC import *
from riot_finder import *
from riot_device_handler import *

cl = []
conf_json = {}
device_list = numpy.array([])
default_addr = "WINDOWS-XX:XX:XX:XX:XX:XX|MAC-/dev/tty.BITalino-XX-XX-DevB"
plux = None

class Utils:
    OS = None
    home = ''
    json_file_path = './static/bit_config.json'
    my_ipv4_addr = ''
    net_interface_type = None
    enable_servers = {"Bluetooth": False, "OSC": False, "UDP_out": False, "Serial": False}

    def add_quote(self, a):
        return '"{0}"'.format(a)

    def getPluxAPI(self):
        try:
            import plux_python3.WIN64.plux  as plux
        except Exception as e:
            try:
                import plux_python3.WIN32.plux as plux
            except Exception as e:
                try:
                    import plux_python3.OSX.plux as plux
                except Exception as e:
                    print (e)
                    try:
                        import plux_python3.LINUX_AMD64.plux as plux
                    except Exception as e:
                        print ("Unable to import PLUX API")
                        return None
        return plux

    def getBioPLUX(self):
        global plux
        plux = self.getPluxAPI()
        if plux is not None:
            from plux_python3.ServerPLUX import BiosignalsPLUX

class Global:
    OSC_Handler = None
    riot_server_ready = False
    all_devices = []
    active_device_list = []
    inactive_device_list = []
    sensor_data_json = [json.dumps({})]
    debug_info = ""
    external_modules = {}

ut = Utils()
session = Global()

def tostring(data):
    """
        :param data: object to be converted into a JSON-compatible `str`
        :type data: any
        :return: JSON-compatible `str` version of `data`

        Converts `data` from its native data type to a JSON-compatible `str`.
        """
    dtype=type(data).__name__
    if dtype=='ndarray':
        if numpy.shape(data)!=(): data=data.tolist() # data=list(data)
        else: data='"'+data.tostring()+'"'
    elif dtype=='dict' or dtype=='tuple':
        try: data=json.dumps(data, sort_keys=True)
        except: pass
    elif dtype=='NoneType':
        data=''
    elif dtype=='str' or dtype=='unicode':
        data=json.dumps(data, sort_keys=True)

    return str(data)

class PLUX_Device_Handler:
    active_device = None
    def __init__(self, _addr, _type):
        self.addr = _addr
        self.type = _type
    def connect(self):
        raise NotImplementedError("function not implimented for this class")

class BITalino_Device(PLUX_Device_Handler):
    ch_mask = srate = None
    def test_connection(self, srate, ch_mask):
        self.ch_mask = ch_mask
        self.srate = srate
        self.active_device = BITalino(self.addr)
        self.active_device.start(self.srate, self.ch_mask)

    def disconnet(self):
        self.active_device.stop()

    async def get_data_json(self, nsamples, labels, dev_index):
        device = self.active_device
        ch_mask = numpy.array(self.ch_mask) - 1
        cols = numpy.arange(len(ch_mask)+5)
        labels = ["nSeq", "I1", "I2", "O1"] + labels
        data = device.read(nsamples)
        res = "{"
        for i in cols:
            idx = i
            if (i > 4): idx = ch_mask[i - 5] + 5
            res += '"' + labels[idx] + '":' + tostring(data[:, i]) + ','
        res = res[:-1] + "}"
        #print(res)
        session.sensor_data_json[0] = res
        if len(json.loads(json.dumps(session.sensor_data_json[0]))) == 0:
            session.sensor_data_json[0] = res
        else:
            session.sensor_data_json[dev_index] = res
        await asyncio.sleep(0.0)

class Riot_Device(PLUX_Device_Handler):
    def test_connection(self):
        print ("could not connect to: %s (%s)" % (self.addr, self.type))

    async def get_data_json(self):
        raise NotImplementedError("function not implimented for this class")

def restart_app():
    time.sleep(1)
    if ut.OS == "windows":
       restart = subprocess.Popen("start_win.bat", shell=True, stdout = subprocess.PIPE)
       stdout, stderr = restart.communicate()
    else:
        sys.exit(1)
#    os_list = ["linux", "windows"]
#    if ut.OS not in os_list:
#        import osx_statusbar_app
#        osx_statusbar_app.restart()
#    elif 'linux' in ut.OS:
#        os.popen("./start_linux.sh")

def change_json_value(file,orig,new,isFinal):
    ##find and replace string in file, keeps formatting
    addComma = ','
    if isFinal: addComma = ''
    for line in fileinput.input(file, inplace=1):
        if orig in line:
            line = line.replace(str(line.split(': ')[1]), str(new.split(': ')[1]) + "%s\n" % addComma)
        sys.stdout.write(line)

# fetch nearby/pairs devices using respective PLUX/Bitalino classes
def listDevices(enable_servers):
    print ("============")
    print ("please select your device:")
    print ("Example: /dev/tty.BITalino-XX-XX-DevB")
    allDevicesFound = deviceFinder.findDevices(ut.OS, enable_servers, session.riot_server_ready)
    if plux is not None:
        allDevicesFound.extend(plux.BaseDev.findDevices())
    dl = []
    for dev in allDevicesFound:
        if "biosignalsplux" not in dev[0] and "BITalino" not in dev[1]:
            dl.append([ut.add_quote(dev[0]), dev[1]])
    allDevicesFound = numpy.array(dl)
    return allDevicesFound

def check_net_config():
    net = riot_net_config(ut.OS, None)
    riot_interface_type = ut.enable_servers['OSC_config']['net_interface_type']
    riot_ssid = ut.enable_servers['OSC_config']['riot_ssid']
    # -2.1- get network interface and ssid & assign module ip
    # -2.2- get serverBIT host ipv4 address
    # -2.3- check host ssid matches that assigned to the R-IoT module
    net_interface_type, ssid = net.detect_net_config(riot_interface_type)
    ipv4_addr = net.detect_ipv4_address(net_interface_type)
    if ssid is None or ssid not in riot_ssid:
        return False
    # -2.4- change host ipv4 to match the R-IoT module if required
    if ut.enable_servers["OSC_config"]["riot_ip"] not in ipv4_addr:
        return False
    return True

class Index(web.RequestHandler):
    def get(self):
        print("config page opened")
        self.render("config.html",
                    crt_conf = json.load(open(ut.json_file_path, 'r')),
                    old_conf = json.load(open('./static/bit_config.json', 'r')),
                    console_text = "ServerBIT Configuration",
                    OSC_config = json.load(open(ut.json_file_path, 'r'))['OSC_config'],
                    riot_labels = json.load(open(ut.json_file_path, 'r'))['riot_labels'],
                    bitalino_address = "/<id>/bitalino",
                    debug_info = session.debug_info
                    )

    def on_message(self, message):
        self.write_message(u"You said: " + message)

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)
        print("CONNECTED")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        if self in cl:
            cl.remove(self)
        print("DISCONNECTED")

class DeviceUpdateHandler(web.RequestHandler):
    def check_origin(self, origin):
        return True

    def post(self):
        # print(self.request.body)
        ut.enable_servers.update(json.loads(self.request.body))

    def open(self):
        if self not in cl:
            cl.append(self)
        print("CONNECTED")

    def get(self):
        device_list = listDevices(ut.enable_servers)
        device_dict = {}
        device_dict['dev_list'] = device_list.tolist()
        device_list = json.dumps(tostring(device_dict))
        device_list = json.loads(device_list)
        #print (device_list)
        self.write(device_list)

class WebConsoleHandler(websocket.WebSocketHandler):
    def get(self):
        net = riot_net_config(ut.OS)
        riot_interface_type = ut.enable_servers['OSC_config']['net_interface_type']
        riot_ssid = ut.enable_servers['OSC_config']['riot_ssid']
        console_str="ServerBIT R-IoT server is ready"
        # -2.1- get network interface and ssid & assign module ip
        time.sleep(1)
        net_interface_type, ssid = net.detect_net_config(riot_interface_type)
        if ssid is None:
            console_str = "Please connect to a WiFi network and try again"
            self.write( json.dumps(console_str) )
            return
        # -2.2- get serverBIT host ipv4 address
        ipv4_addr = net.detect_ipv4_address(net_interface_type)

        # -2.3- check host ssid matches that assigned to the R-IoT module
        if ssid not in riot_ssid:
            print ('{:^24s}'.format("====================="))
            console_str = "currently connected to '%s', please connect to the same network as the R-IoT (%s)" % (ssid, riot_ssid)
            self.write( json.dumps(console_str) )
            return

        # -2.4- change host ipv4 to match the R-IoT module if required
        if ut.enable_servers["OSC_config"]["riot_ip"] not in ipv4_addr:
            console_str = ("The computer's IPv4 address must be changed to match \nrun the following command to reconfigure your wireless settings ||| Continue")
            ut.my_ipv4_addr = ipv4_addr
            ut.net_interface_type = net_interface_type
            ut.riot_server_ready = True
            self.write( json.dumps(console_str) )

            def post(self):
                net = riot_net_config(ut.OS)
                console_return = json.loads((self.request.body).decode('utf-8'))
                if "Continue" in console_return["msg"]:
                    console_str = net.reconfigure_ipv4_address(ut.enable_servers["OSC_config"]["riot_ip"], ut.my_ipv4_addr, ut.net_interface_type)
                    console_str += " ||| Run Command"
                    self.write( json.dumps(console_str) )
                    return

                if "Run Command" in console_return["msg"]:
                    console_str = riot_net_config.run_ifconfig_command (console_return["cmd"])
                    self.write(json.dumps(console_str))
                    return

class Configs(web.RequestHandler):
    def get(self):
        self.write(conf_json)

    def post(self):
        new_config = json.loads(self.request.body)
        if "restored config.json" in new_config:
            print("restoring current configuration")
            try:
                rmtree(ut.home)
            except:
                pass
        else:
            for key, old_value in conf_json.items():
                format = str('"' + key + '": ')
                if "riot_labels" in key:
                    continue
                if "OSC_config" in key:
                    continue
                new_value = format + str(new_config[key])
                #string attribute
                if isinstance(old_value, str):
                    old_value = format + ut.add_quote(str(old_value))
                #list of strings
                if all(isinstance(n, str) for n in new_config[key]):
                    old_value = format + str(old_value).replace("'", '"')
                    new_value = format + str(new_config[key]).replace("'", '"')
                #boolean attribute
                # if isinstance(old_value, bool):
                #     old_value = format = str(old_value).lower()
                #     new_value = format = str(new_value).lower()
                else:
                    old_value = format + str(old_value)
                if new_value not in old_value:
                    print (old_value)
                    print ("writing to json:" + new_value)
                    change_json_value(ut.json_file_path, format, str(new_value), "OSC_config" in key)
        restart_app()

def signal_handler(signal, frame):
    print('TERMINATED')
    sys.exit(0)

def start_gui():
    os_list = ["linux", "windows"]
    if ut.OS not in os_list:
        import osx_statusbar_app

def getConfigFile():
    try:
        with open(ut.home+'/config.json') as data_file:
            conf_json = json.load(data_file)
            ut.json_file_path = ut.home + '/config.json'
            return conf_json
    except Exception as e:
        print(e)
        session.debug_text = e
        with open('config.json') as data_file:
            conf_json = json.load(data_file)
            os.mkdir(ut.home)
        os.mkdir(ut.home+'/static')
        os.mkdir(ut.home+'/modules')
        copyfile('config.json', ut.home + '/config.json')
        ut.json_file_path = ut.home + '/config.json'
        for file in ['ClientBIT.html', 'static/jquery.flot.js', 'static/jquery.js', 'Preferences.html', 'modules/modules.txt']:
            with open(ut.home+'/'+file, 'w') as outfile:
                outfile.write(open(file).read())
        restart_app()

def dynamic_import(abs_module_path, class_name):
    module_object = import_module(abs_module_path)
    target_class = getattr(module_object, class_name)
    return target_class

def import_modules():
    print ("<checking for new modules>")
    print ("importing the following modules to ServerBIT:")
    modules_path = ut.home + '/modules/'
    sys.path.insert(0, modules_path)
    module_folders = [f.name for f in os.scandir(modules_path) if f.is_dir() ]
    module_folders.remove('__pycache__')
    for folder_dir in module_folders:
        for file in os.listdir(modules_path + folder_dir):
            if file.endswith(".py"):
                module_name = os.path.splitext(file)[0]
                module_script = module_name + '.' + module_name
                found_script = importlib.util.find_spec(module_script)
                if found_script is not None:
                    print(module_script)
                    session.external_modules[module_name] = dynamic_import(module_script, module_name)
# arduino_controller = session.external_modules["OSC_Serial_Controller"]()
# print(arduino_controller.baud_rate)

def check_device_addr(addrs):
    new_device = None
    if default_addr in addrs:
        print ("device address has not been added" + "\n" + "please select a PLUX device in the device finder")
        while new_device is None:
            time.sleep(1)
            pass
    for mac_addr, type in addrs:
        print(mac_addr)
        try:
            #type = deviceFinder.check_type(str(mac_addr))
            if 'bitalino' in type.lower():
                session.all_devices.append(BITalino_Device(mac_addr, type))
            elif 'r-iot (osc)' in type.lower():
                session.all_devices.append(Riot_Device(mac_addr, type))
        except Exception as e:
            pass
        print ("connecting to %s ..." % session.all_devices)
        return addrs

async def connect_devices(all_devices, ch_mask, srate, wait_time=None):
    ch_mask = numpy.array(ch_mask) - 1
    for device in all_devices:
        mac_addr = str(device.addr)
        try:
            device.test_connection(srate, ch_mask)
            session.active_device_list.append(device)
            print('new device connected %s' % mac_addr)
            if mac_addr in session.inactive_device_list:
                session.inactive_device_list.remove(mac_addr)
        except Exception as e:
            print(e)
            print ("could not connect to: %s" % mac_addr)
            session.debug_info = e
            if mac_addr not in session.inactive_device_list:
                session.inactive_device_list.append(mac_addr)
            await asyncio.sleep(2.0)
            continue # move onto next device in list
    wait_time = 0.0 if wait_time is None else wait_time
    await asyncio.sleep(wait_time)
    return

async def print_device_data():
    if (sum(dev is not None for dev in session.active_device_list) and sum(pak is not json.dumps({}) for pak in session.sensor_data_json)):
        for i in range(len(session.sensor_data_json)):
            print(session.sensor_data_json[i])
        print(len(session.sensor_data_json))

async def main_device_handler(all_devices, ch_mask, srate, nsamples, labels):
    # riot = riot_handler()
    active_device_list = []
    # 1. first attempt to connect all devices
    ip, port = ut.enable_servers['OSC_config']['riot_ip'], ut.enable_servers['OSC_config']['riot_port']
    while len(session.active_device_list) == 0:
        await connect_devices(all_devices, ch_mask, srate)
        # ut.active_device_list.extend(riot.fetch_devices(ip, port, 1))
        await asyncio.sleep(5)
    # 2. re-attept to connect / restart dropped connections
    # 2.1 update device list upon new connection
    # while True:
    #     await connect_devices(session.inactive_device_list, ch_mask, srate, riot, wait_time=0.0)
    if active_device_list != session.active_device_list:
        print("updating device list")
        active_device_list = session.active_device_list
    # 3. begin data acquisition
    print (active_device_list)
    while True:
        dev_index = 0
        device = active_device_list[dev_index]
        try:
            #                print('streaming from: %s (%s)' % (device.addr, dev_index))
            await device.get_data_json(nsamples, labels, dev_index)
        #await print_device_data()
        except Exception as e:
            print(e)
            print ("connection to %s dropped" % device.addr)
            session.debug_text = e
            session.active_device_list.remove(device) # remove device connection
            session.inactive_device_list.append(str(device.addr))
            device.active_device = None
            pass
    if len(session.active_device_list) != 0:
        return

# loop to continuously send data via Websockets
async def WebSockets_Data_Handler(ws, path):
    print('LISTENING')
    print(ws.port)
    # print ("streaming data from device to %s:%i" % (path, ws.port))
    while True:
        if (sum(dev is not None for dev in session.active_device_list) and sum(pak is not json.dumps({}) for pak in session.sensor_data_json)):
            await ws.send(session.sensor_data_json[0])
        else:
            print('waiting for data')
            await asyncio.sleep(3.0)
        await asyncio.sleep(0.1)

async def OSC_Data_Handler():
    while 1:
        # await session.OSC_Handler.sendTestBundle(5)
        if (sum(dev is not None for dev in session.active_device_list) and sum(pak is not json.dumps({}) for pak in session.sensor_data_json)):
            if (conf_json ['consolidate_outputs'] == False):
                await session.OSC_Handler.output_bundle(session.sensor_data_json)
            else:
                await session.OSC_Handler.output_individual(session.sensor_data_json)
        else:
            print('waiting for data')
            await asyncio.sleep(3.0)
        await asyncio.sleep(0.0)

# Run configuration web page in the background
class ConfigWebServer(threading.Thread):
    def run(self):
        conf_port = 9001
        asyncio.set_event_loop(asyncio.new_event_loop())
        settings = {"static_path": os.path.join(os.path.dirname(__file__), "static")}
        app = web.Application([(r'/', SocketHandler), (r'/config', Index), (r'/v1/devices', DeviceUpdateHandler), (r'/v1/console', WebConsoleHandler), (r'/v1/configs', Configs)], **settings)
        # signal.signal(signal.SIGINT, signal_handler)
        app.listen(conf_port)
        ioloop.IOLoop.instance().start()

ConfigWebServer().start()

if __name__ == '__main__':
    # ut.getBioPLUX()
    ut.OS = platform.system().lower()
    print ("Detected platform: " + ut.OS)
    ut.home = expanduser("~") + '/ServerBIT'
    start_gui()
    try:
        conf_json = getConfigFile()
        conf_json['OSC_config'][1] = int(conf_json ['OSC_config'][1])
        ut.enable_servers['OSC_config'] = {
            "riot_ip": conf_json['OSC_config'][0],
            "riot_port": conf_json['OSC_config'][1],
            "riot_ssid": conf_json['OSC_config'][2],
            "net_interface_type": conf_json['OSC_config'][3]
        }
    except KeyError as ke:
        session.debug_info = "invalid json file in %s" % ut.json_file_path
        print ("invalid json file in %s" % ut.json_file_path)
        rmtree(ut.home)
        restart_app()
    print("data received")
    print("home folder %s" % ut.json_file_path)
    # import_modules()
    # check device id, wait for valid selection
    new_mac_addr = check_device_addr(conf_json['device'])
    main_device_loop = asyncio.get_event_loop()
    time.sleep(5.0)
    if not session.riot_server_ready and any(isinstance(dev, Riot_Device) for dev in session.all_devices):
        print ("Network needs to be re-configured. Go to Preferences.html for assistance")
        while not session.riot_server_ready:
            session.riot_server_ready = check_net_config()
            time.sleep(1.0)
    else:
        time.sleep(3.0)
    if 'websockets' in conf_json['protocol'].lower():
        start_server = websockets.serve(WebSockets_Data_Handler, '0.0.0.0', conf_json['port'])
    elif 'osc' in conf_json['protocol'].lower():
        session.OSC_Handler = OSC_Handler(conf_json['ip_address'], conf_json['port'], conf_json['labels'])
    try:
        if 'websockets' in conf_json['protocol'].lower():
            main_device_loop.run_until_complete(start_server)
        elif 'osc' in conf_json['protocol'].lower():
            session.debug_info="main loop started"
            main_device_loop.create_task(OSC_Data_Handler())
        for module_name, module_class in session.external_modules.items():
            continue
        main_device_loop.create_task(main_device_handler(session.all_devices, conf_json['channels'], conf_json['sampling_rate'], conf_json['buffer_size'], conf_json['labels']))
        main_device_loop.run_forever()
    except Exception as e:
        print(e)
        session.debug_info = e
        pass
    finally:
        for dev_index, device in enumerate(session.active_device_list):
            device.disconnet()
        main_device_loop.stop()
