""" OSC server ofr BITalino R-IoT

"""
import argparse
import math

from tornado import websocket, web, ioloop
import _thread as thread
import asyncio
import websockets
import json
import signal
import numpy
import sys, traceback, os, time, platform
import subprocess
#from os.path import expanduser

from pythonosc import dispatcher
from pythonosc import osc_server
import netifaces

net_interface_type = "en0"
riot_ip = '192.168.1.100'
riot_ssid = 'riot'

class Utils:
    OS = None
    device_data = [""] # 1 json string for each device
    #device_ids = [0]
    device_ids = ['/0/raw']
    num_devices = len(device_ids)
    osc_server_started = False
    riot_labels = ["ACC_X", "ACC_Y", "ACC_Z", "GYRO_X", "GYRO_Y", "GYRO_Z", "MAG_X", "MAG_Y", "MAG_Z",
        "TEMP", "IO", "A1", "A2", "C", "Q1", "Q2", "Q3", "Q4", "PITCH", "YAW", "ROLL", "HEAD"]
    riot_channels = list(range(23))[1:]

ut = Utils()

def new_device(n):
    print ("new device connected!")
    ut.device_ids.append('/%s/raw' % n)
    ut.device_data.append("") #assign empty string to each device

def assign_riot_data(msg_addr, *values):
    # d_id = (int(unused_addr[1]))
    d_id = msg_addr
    if d_id not in ut.device_ids: new_device(d_id)

    channels = ut.riot_channels
    labels = ut.riot_labels
    ch_mask = numpy.array(channels) - 1
    try:
        cols = numpy.arange(len(ch_mask))
        res = "{"
        for i in cols:
            res += '"' + labels[i] + '":' + str(values[i]) + ','
        res = res[:-1] + "}"
        #if len(cl) > 0: cl[-1].write_message(res)
        ut.device_data[int(d_id[1])] = res
    except:
        traceback.print_exc()
        os._exit(0)

def start_riot_listener(ip, port):
    riot_dispatcher = dispatcher.Dispatcher()
    riot_dispatcher.map("/*/raw", assign_riot_data)
    # riot_dispatcher.map("/*/bitalino", assign_bitalino_data)

    server = osc_server.ThreadingOSCUDPServer(
      (ip, port), riot_dispatcher)
    print("Serving on {}".format(server.server_address))
    ut.osc_server_started = True
    server.serve_forever()

def detect_net_config(net_interface_type, OS):
    if net_interface_type is not None:
        net_interface_type, ssid = detect_wireless_interface(OS, [net_interface_type])
    while net_interface_type is None:
        try:
            print ("detecting wireless interface... (this can be set manually with --net)")
            net_interface_type, ssid = detect_wireless_interface(OS, netifaces.interfaces())
        except:
            print ("could not retrieve ssid from %s" % net_interface_type)
            print ("see available interfaces with: \n \
                ifconfig -a (UNIX) \n ipconfig |findstr 'adapter' (WINDOWS)")
            print ('{:^24s}'.format("====================="))
            input ("please connect to a Wi-Fi network and press ENTER to continue")
    return net_interface_type, ssid

def detect_wireless_interface(OS, interface_list):
    det_interface = det_ssid = None
    for interface in interface_list:
        if ("linux" in OS):
            det_interface = os.popen('iwgetid').read()[:-1].split()[0]
            det_ssid = os.popen('iwgetid -r').read()[:-1]
            break
        elif ("windows" in OS):
            det_interface = os.popen('netsh wlan show interfaces | findstr /r "^....Name"').read()[:-1].split()[-1]
            det_ssid = os.popen('netsh wlan show interfaces | findstr /r "^....SSID"').read()[:-1].split()[-1]
            break
        else:
            ssid = os.popen('networksetup -getairportnetwork ' + interface).read()[:-1]
            if '** Error: Error obtaining wireless information' not in ssid:
                det_ssid = ssid[23:]
                det_interface = interface
                break

    return det_interface, det_ssid

def update_progress(count, total, status=''):
    bar_len = 20
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()
def timer(t, rate = 0.25, text=''):
    tt=round((t+rate)/rate)
    for i in range(tt):
        update_progress(i, round(t/rate), text)
        time.sleep(rate)
    print("\n")

def reset():
    time.sleep(0.5)
    os.execl(sys.executable, os.path.abspath(_file_), *sys.argv)

async def webApp(ws, path):
    device_id = ws.port - 9001
#    print('LISTENING')
    print (ut.device_data[device_id])
    print ("streaming data from device %i to port %i" % (device_id, ws.port))
    while ut.device_data[device_id] != "":
        await ws.send(ut.device_data[device_id])
        await asyncio.sleep(0.1)

# if __name__ == "__main__":
    # -1- parse arguemnts
    '''

    OS = platform.system()
    parser = argparse.ArgumentParser()
    parser.add_argument("--id",
      type=int, default=0, help="This dictates the OSC reveive address: /<id>/raw")
    parser.add_argument("--ip",
      default=riot_ip, help="The ip to listen on (usually set to 192.168.1.00)")
    parser.add_argument("--port",
      type=int, default=8888, help="The port to listen on")
    parser.add_argument("--ssid",
      default=riot_ssid, help="name of the wifi network which R-IoT device is streaming data to")
    parser.add_argument("--net_interface",
      default=None, help="name of the wireless interface which the computer is using")
    parser.add_argument("--websockets_ip",
      default='127.0.0.1', help="destination ip for websocket handler")
    parser.add_argument("--websockets_port",
      type=int, default=9001, help="destination port for websocket handler is the port + device ID")
    parser.add_argument("--find_new",
      type=int, default=1, help="find new devices in network")
    args = parser.parse_args()

    # -2- network config
    net_interface_type, ssid = detect_net_config(args.net_interface, OS)
    print("Connected to wifi network: " + ssid)

    if riot_ip not in args.ip:
        print ("IP address changed from R-IoT default (%s)" % riot_ip)

    if "Windows" in OS:
            ipv4_addr = os.popen('netsh interface ipv4 show config %s | findstr /r "^....IP Address"' % net_interface_type).read()[:-1].split()[-1]
            print("Network interface %s address: %s" % (net_interface_type, ipv4_addr))
    else:
        addrs = netifaces.ifaddresses(net_interface_type)
        ipv4_addr = addrs[netifaces.AF_INET][0]['addr']
        print("Network interface %s address: %s" % (net_interface_type, ipv4_addr))

    while ssid not in args.ssid:
        print ('{:^24s}'.format("====================="))
        print ("currently connected to '%s', please connect to the same network as the R-IoT (%s)" % (ssid, args.ssid))
#        print ("(target ssid can be changed with --ssid 'name_of_network')")
        input("please re-open R-IoT_ServerBIT or press ENTER to retry")
        net_interface_type, ssid = detect_net_config(args.net, OS)

    if args.ip not in ipv4_addr:
        print ("The computer's IPv4 address must be changed to match")
#        print(">>> use the following command")
        if "Windows" in OS:
            cmd = "netsh interface ip set address %s static %s 255.255.255.0 192.168.1.1" % (net_interface_type, args.ip)
#            print(cmd)
#            print("(run as administrator)")
            input("press ENTER to auto re-configure network settings and continue. You may need to re-open R-IoT serverBIT")
#            subprocess.Popen(cmd)
            try:
                proc = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
                timer(3)
                # do something with output
            except subprocess.CalledProcessError:
                input ("There was an error, please run as administrator. You can also change the ipv4 address manually (see R-IoT guide)  \
                \nclose window and try again")
                sys.exit(1)
        else:
            cmd = "sudo ifconfig %s %s netmask 255.255.255.0" % (net_interface_type, riot_ip)
            print(">>> paste the following command")
            print ( cmd )
            raise Exception()
    #        exit()
    print ("Starting riot_serverBIT...")
    timer(2)

    '''

# -3- stream device data to network
def fetch_devices(listener_ip, listener_port, find_new):
    osc_devices = []
    max_counter = 0
    try:
        thread.start_new_thread(start_riot_listener, (listener_ip, listener_port)) # one thread to listen to all devices on the same ip & port
        while not ut.osc_server_started : time.sleep(0.1)
        if find_new == 1: timer(5, text="searching for devices on this network")
        while ut.device_data[0] == "" or len(ut.device_ids) == 0 or max_counter < 2:
            print ("no devices found")
            timer(5, text="searching for devices on this network")
            max_counter+=1
        print ("found %i device(s)" % len(ut.device_ids))
        for device_id in ut.device_ids:
            osc_devices.append([str(device_id), "R-Iot (OSC)"])
        return osc_devices
        # asyncio.get_event_loop().run_forever()
    except Exception as e:
        print (e)
        return 0
    # finally:
    #     print ()
    #     sys.exit(1)
