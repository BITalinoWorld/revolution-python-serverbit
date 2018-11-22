from tornado import websocket, web, ioloop
import thread
import json
import signal
import sys
import numpy
import time
import sys, traceback, os
from bitalino import *
from os.path import expanduser

plux = None
device_data = []
cl = []
bioplux_devices = []

# -*- Uncommet to use configuration from script (ignores config.json)
# -*- You will also need to uncomment the line below: "config = conf_json"
'''
conf_json = {
	"device": ["00:07:80:3B:46:58"],
	"channels": [1, 2, 6],
	"sampling_rate": 1000,
	"buffer_size": 10,
	"labels": ["nSeq", "CH1","CH2","CH3","CH4","CH5","CH6","CH7","CH8"],
	"port": 9001
}
'''

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
        try: data=json.dumps(data)
        except: pass
    elif dtype=='NoneType':
        data=''
    elif dtype=='str' or dtype=='unicode':
        data=json.dumps(data)

    return str(data)

def getPluxAPI():
    try:
        import WIN64.plux  as plux
    except Exception as e:
        try:
            import WIN32.plux as plux
        except Exception as e:
            try:
                import OSX.plux as plux
            except Exception as e:
                print (e)
                try:
                    import LINUX_AMD64.plux as plux
                except Exception as e:
                    print ("Unable to import PLUX API")
                    return None
    return plux

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

def signal_handler(signal, frame):
    print('TERMINATED')
    sys.exit(0)

# def BITalino_handler(mac_addr, ch_mask, srate, labels):
#     ch_mask = numpy.array(ch_mask)-1
#     try:
#         print(mac_addr)
#         device=BITalino(mac_addr)
#         print(ch_mask)
#         print(srate)
#         device.start(srate, ch_mask)
#         cols = numpy.arange(len(ch_mask)+5)
#         while (1):
#             data=device.read(250)
#             res = "{"
#             for i in cols:
#                 idx = i
#                 if (i>4): idx=ch_mask[i-5]+5
#                 res += '"'+labels[idx]+'":'+tostring(data[:,i])+','
#             res = res[:-1]+"}"
#             if len(cl)>0: cl[-1].write_message(res)
#     except:
#         traceback.print_exc()
#         os._exit(0)

def BioPLUX_handler(mac_addr, ch_mask, srate, labels):
    bioplux_ch_mask = []
    bioplux_labels = [labels[0]]
    for ch in ch_mask:
        bioplux_source = plux.Source()
        bioplux_source.port = ch
        bioplux_ch_mask.append(bioplux_source)
        bioplux_labels.append(labels[ch])
    try:
        device = BiosignalsPLUX(mac_addr)
        device.labels = bioplux_labels
        device.cols = numpy.insert(numpy.arange(len(ch_mask))+1, 0, 0)
        device_props = device.getProperties()
        print (device_props)
        device.start(srate, (bioplux_ch_mask))
        global bioplux_devices
        bioplux_devices.append(device)
        device.loop()
    except:
        traceback.print_exc()
        os._exit(0)

def data_handler(device):
    labels, cols = device.labels, device.cols
    print(cols)
    while True:
        data = list(device.read())
        if data != device.prev_data_buffer:
            res = "{"
            for i in cols:
                res += '"'+labels[i]+'":'+tostring([nSeq[i] for nSeq in data])+','
            res = res[:-1]+"}"
            if len(cl)>0: cl[-1].write_message(res)
            device.request_new_seq(data)

app = web.Application([(r'/', SocketHandler)])

if __name__ == '__main__':
    plux = getPluxAPI()
    if plux is not None:
        from biosignalsPLUX import BiosignalsPLUX
    # -*- Uncomment to list nearby devices in console
    # print(plux.BaseDev.findDevices())
    home = expanduser("~") + '/ServerBIT'
    print(home)
    try:
        with open(home+'/config.json') as data_file:
            config = json.load(data_file)
    except:
        with open('config.json') as data_file:
            config = json.load(data_file)
        os.mkdir(home)
        with open(home+'/config.json', 'w') as outfile:
            json.dump(config, outfile)
        for file in ['ClientBIT.html', 'jquery.flot.js', 'jquery.js']:
            with open(home+'/'+file, 'w') as outfile:
                outfile.write(open(file).read())
    # -*- Uncomment to use configuration from script (ignores config.json)
    # config = conf_json
    signal.signal(signal.SIGINT, signal_handler)
    app.listen(config['port'])
    print('LISTENING')
    for device_addr in config['device']:
        device_addr = str(device_addr)
        thread.start_new_thread(BioPLUX_handler, (device_addr,config['channels'],config['sampling_rate'], config['labels']))
    while len(bioplux_devices) == 0:
        time.sleep(1.0)
        print("waiting for device connection...")
    for bioplux_device in bioplux_devices:
        thread.start_new_thread(data_handler, (bioplux_device,))
    ioloop.IOLoop.instance().start()
