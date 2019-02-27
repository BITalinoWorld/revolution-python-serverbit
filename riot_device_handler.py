""" OSC server ofr BITalino R-IoT

"""
import argparse
import math

from tornado import websocket, web, ioloop
import _thread as thread
import asyncio, sys, time
import json
import numpy

from pythonosc import dispatcher
from pythonosc import osc_server

class riot_handler:
    device_data = [""] # 1 json string for each device
    device_ids = ['/0/raw']
    num_devices = len(device_ids)
    osc_server_started = False
    riot_labels = ["ACC_X", "ACC_Y", "ACC_Z", "GYRO_X", "GYRO_Y", "GYRO_Z", "MAG_X", "MAG_Y", "MAG_Z",
        "TEMP", "IO", "A1", "A2", "C", "Q1", "Q2", "Q3", "Q4", "PITCH", "YAW", "ROLL", "HEAD"]
    riot_channels = list(range(23))[1:]
    ip = ""
    port = 8080
    protocol = "OSC"

    def new_device(self, n):
        print ("new device connected!")
        self.device_ids.append('%s' % n)
        self.device_data.append("") #assign empty string to each device

    def assign_riot_data(self, msg_addr, *values):
        # d_id = (int(unused_addr[1]))
        d_id = msg_addr
        if d_id not in self.device_ids: self.new_device(d_id)

        channels = self.riot_channels
        labels = self.riot_labels
        ch_mask = numpy.array(channels) - 1
        try:
            cols = numpy.arange(len(ch_mask))
            res = "{"
            for i in cols:
                res += '"' + labels[i] + '":' + str(values[i]) + ','
            res = res[:-1] + "}"
            #if len(cl) > 0: cl[-1].write_message(res)
            self.device_data[int(d_id[1])] = res
            print(self.device_data[0])
        except:
            traceback.print_exc()
            os._exit(0)

    def start_riot_listener(self, ip, port):
        riot_dispatcher = dispatcher.Dispatcher()
        riot_dispatcher.map("/*/raw", self.assign_riot_data)
        # riot_dispatcher.map("/*/{raw, bitalino}", assign_bitalino_data)

        server = osc_server.ThreadingOSCUDPServer(
          (ip, port), riot_dispatcher)
        print("Serving on {}".format(server.server_address))
        self.osc_server_started = True
        server.serve_forever()

    # async def webApp(ws, path):
    #     device_id = ws.port - 9001
    # #    print('LISTENING')
    #     print (ut.device_data[device_id])
    #     print ("streaming data from device %i to port %i" % (device_id, ws.port))
    #     while ut.device_data[device_id] != "":
    #         await ws.send(ut.device_data[device_id])
    #         await asyncio.sleep(0.1)

    def testApp():
        thread.start_new_thread(self.start_riot_listener, (self.ip , self.port)) # one thread to listen to all devices on the same ip & port

    # -3- stream device data to network
    def fetch_devices(self, listener_ip, listener_port, find_new):
        self.ip = listener_ip
        self.port = listener_port
        osc_devices = []
        max_counter = 0
        try:
            thread.start_new_thread(self.start_riot_listener, (listener_ip, listener_port)) # one thread to listen to all devices on the same ip & port
            while not self.osc_server_started : time.sleep(0.1)
            if find_new == 1: timer(5, text="searching for devices on this network")
            while self.device_data[0] == "" or len(self.device_ids) == 0:
                print ("no new devices found")
                timer(5, text="searching for devices on this network")
                max_counter+=1
                if max_counter > 2:
                    return []
            print ("found %i device(s)" % len(self.device_ids))
            for device_id in self.device_ids:
                osc_devices.append([str(device_id), "R-Iot (OSC)"])
            return osc_devices
        except Exception as e:
            print (e)
            return []
        # finally:
        #     print ()
        #     sys.exit(1)

    def read_data(self):
        # print(self.device_data[0])
        main_device_loop = asyncio.get_event_loop()
        try:
            main_device_loop.run_until_complete(testApp())
        except Exception as e:
            print(e)
        finally:
            main_device_loop.stop()

def update_progress(count, total, status=''):
    # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)
    bar_len = 20
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def timer(t, rate = 0.25, text=''):
    tt=round((t+rate)/rate)
    for i in range(tt):
        update_progress(i, round(t/rate), text)
        time.sleep(rate)
    print("\n")
