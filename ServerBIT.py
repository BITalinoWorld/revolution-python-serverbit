from tornado import websocket, web, ioloop
# import thread
import _thread as thread
import json
import signal
import sys
import numpy
import time
import sys, traceback, os
from bitalino import *
from os.path import expanduser

import deviceFinder as deviceFinder
import fileinput, time
from shutil import copyfile

cl = []
conf_json = {}
home = ''
device_list = numpy.array([])
json_file_path = './static/bit_config.json'
default_addr = "WINDOWS-XX:XX:XX:XX:XX:XX|MAC-/dev/tty.BITalino-XX-XX-DevB"
conf_port = 9001

class Utils:
    OS = None
    enable_servers = {"BITalino": 'true', "Riot": 'false'}
    BITalino_device = None
    USE_GUI = True
    sensor_data_json = ""
    labels = ["nSeq", "I1", "I2", "O1", "O2","A1","A2","A3","A4","A5","A6"]

    def add_quote(self, a):
        return '"{0}"'.format(a)

    def strToBool(self, v):
        try:
            return v.lower() in ("True", "true", "1")
        except Exception as e:
            return v

    def jsonToBool(self, json):
        for key, bool in json.items():
            json[key] = self.strToBool(bool)
        return json

ut = Utils()

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

def change_json_value(file,orig,new):
    ##find and replace string in file, keeps formatting
    # print(file, orig, new)
    for line in fileinput.input(file, inplace=1):
        if orig in line:
            line = line.replace(orig, new)
        sys.stdout.write(line)

class Index(web.RequestHandler):
    def get(self):
        self.render("config.html",
            crt_conf = json.load(open(json_file_path, 'r')),
            old_conf = json.load(open('./static/bit_config.json', 'r')),
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
        print(self.request.body)
        ut.enable_servers = json.loads(self.request.body)
        ut.enable_servers = ut.jsonToBool(ut.enable_servers)

    def open(self):
        self.write("device_list")
        if self not in cl:
            cl.append(self)
        print("CONNECTED")


    def get(self):
        device_list = listDevices(ut.enable_servers)
        device_dict = {}
        device_dict['dev_list'] = device_list.tolist()
        device_list = json.dumps(tostring(device_dict))
        device_list = json.loads(device_list)
        print (device_list)
        self.write(device_list)

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        if self in cl:
            cl.remove(self)
        print("DISCONNECTED")

class DeviceFinderHandler(web.RequestHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("CONNECTED")

    def post(self):
        print(self.request.body)
        ut.enable_servers = json.loads(self.request.body)
        ut.enable_servers = ut.jsonToBool(ut.enable_servers)

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        if self in cl:
            cl.remove(self)
        print("DISCONNECTED")

class Configs(web.RequestHandler):
    def get(self):
    	self.write(conf_json)

    def post(self):
        # print(self.request.body)
        new_config = json.loads(self.request.body)
        if "restored config.json" in new_config:
            print("resetting")
            return
        ut.BITalino_device = new_config['device'].replace('"', '')
        for key, old_value in conf_json.items():
            format = str('"' + key + '": ')
            new_value = format + str(new_config[key])
            if "device" in key or "protocol" in key:
                old_value = format + ut.add_quote(str(old_value))
            else:
                old_value = format + str(old_value)
            if new_value not in old_value:
                print (old_value)
                print ("writing to json:" + new_value)
                change_json_value(json_file_path, old_value, str(new_value))
        # sys.exit(1)

def signal_handler(signal, frame):
    print('TERMINATED')
    sys.exit(0)

def listDevices(enable_servers):
    print ("============")
    print ("please select your device:")
    print ("Example: /dev/tty.BITalino-XX-XX-DevB")
    if(enable_servers["Bluetooth"]):
        print("listing PLUX devices")
    if(enable_servers["OSC"]):
        print("listing Riot devices")
    allDevices = deviceFinder.findDevices(ut.OS, enable_servers)
    dl = []
    for dev in allDevices:
        dl.append([ut.add_quote(dev[0]), dev[1]])
    allDevices = numpy.array(dl)
    return allDevices

def BITalino_handler(mac_addr, ch_mask, srate, labels):
    new_mac_addr = check_device_addr(mac_addr)
    print('LISTENING')
    #labels = ["'nSeq'", "'I1'", "'I2'", "'O1'", "'O2'", "'A1'", "'A2'", "'A3'", "'A4'", "'A5'", "'A6'"]
    ch_mask = numpy.array(ch_mask) - 1
    try:
        print(new_mac_addr)
        device=BITalino(new_mac_addr)
        print(ch_mask)
        print(srate)
        device.start(srate, ch_mask)
        cols = numpy.arange(len(ch_mask)+5)
        while (1):
            data=device.read(250)
            res = "{"
            for i in cols:
                idx = i
                if (i>4): idx=ch_mask[i-5]+5
                res += '"'+labels[idx]+'":'+tostring(data[:,i])+','
            res = res[:-1]+"}"
            if len(cl)>0: cl[-1].write_message(res)
    except:
        traceback.print_exc()
        os._exit(0)

def check_device_addr(addr):
    new_device = None
    if default_addr in addr:
        while new_device is None:
            new_device = ut.BITalino_device
            addr = new_device
    print ("connecting to %s ..." % addr)
    return addr

settings = {"static_path": os.path.join(os.path.dirname(__file__), "static")}
app = web.Application([(r'/', SocketHandler), (r'/config', Index), (r'/v1/devices', DeviceUpdateHandler), (r'/v1/finders', DeviceFinderHandler), (r'/v1/configs', Configs)], **settings)

if __name__ == '__main__':
    ut.OS = platform.system()
    print ("Detected platform: " + ut.OS)
    home = expanduser("~") + '/ServerBIT'
    print(home)
    try:
        with open(home+'/config.json') as data_file:
            conf_json = json.load(data_file)
            json_file_path = home + '/config.json'
    except Exception as e:
        # print(e)
        with open('config.json') as data_file:
            conf_json = json.load(data_file)
            os.mkdir(home)
        os.mkdir(home+'/static')
        copyfile('config.json', home + '/config.json')
    	# with open(home+'/config.json', 'w') as outfile:
        #     json.dump(conf_json, outfile)
        json_file_path = home + '/config.json'
        for file in ['ClientBIT.html', 'static/jquery.flot.js', 'static/jquery.js']:
        	with open(home+'/'+file, 'w') as outfile:
        		outfile.write(open(file).read())

    # print(conf_json)
    signal.signal(signal.SIGINT, signal_handler)
    app.listen(conf_port)
    # thread.start_new_thread(BITalino_handler, (conf_json['device'],conf_json['channels'],conf_json['sampling_rate'], conf_json['labels']))
    ioloop.IOLoop.instance().start()
