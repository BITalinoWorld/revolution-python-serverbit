import subprocess
from pythonosc import dispatcher
from pythonosc import osc_server
import netifaces

import sys, traceback, os, time

class riot_net_config():
    def __init__(self, OS):
        self.OS = OS
    def detect_net_config(self, net_interface_type):
        if net_interface_type is not None:
            net_interface_type, ssid = detect_wireless_interface(self.OS, [net_interface_type])
        if net_interface_type is None:
            # try:
            print ("detecting wireless interface... (this can be set manually with --net)")
            net_interface_type, ssid = self.detect_wireless_interface(netifaces.interfaces(), self.OS)
            if ssid is not None:
                print("Connected to wifi network: " + ssid)
        return net_interface_type, ssid

    def detect_wireless_interface(self, interface_list, OS):
        det_interface = det_ssid = None
        for interface in interface_list:
            if ("linux" in OS or "Linux" in OS):
                det_interface = os.popen('iwgetid').read()[:-1].split()[0]
                det_ssid = os.popen('iwgetid -r').read()[:-1]
                break
            elif ("Windows" in OS):
                det_interface = os.popen('netsh wlan show interfaces | findstr /r "^....Name"').read()[:-1].split()[-1]
                det_ssid = os.popen('netsh wlan show interfaces | findstr /r "^....SSID"').read()[:-1].split()[-1]
                break
            else:
                ssid = os.popen('networksetup -getairportnetwork ' + interface).read()[:-1]
                if '** Error: Error obtaining wireless information' not in ssid:
                    if len(ssid.split(': ')) > 1:
                        det_ssid = ssid.split(': ')[1]
                        det_interface = interface
                        break
        return det_interface, det_ssid

    def detect_ipv4_address(self, net_interface_type):
        if "Windows" in self.OS:
                ipv4_addr = os.popen('netsh interface ipv4 show config %s | findstr /r "^....IP Address"' % net_interface_type).read()[:-1].split()[-1]
                print("Network interface %s address: %s" % (net_interface_type, ipv4_addr))
        else:
            addrs = netifaces.ifaddresses(net_interface_type)
            ipv4_addr = addrs[netifaces.AF_INET][0]['addr']
            print("Network interface %s address: %s" % (net_interface_type, ipv4_addr))
        return ipv4_addr

    def reconfigure_ipv4_address(self, riot_ip, ipv4_addr, net_interface_type):
        if riot_ip not in ipv4_addr:
            print ("The computer's IPv4 address must be changed to match")
            if "Windows" in self.OS:
                cmd = "netsh interface ip set address %s static %s 255.255.255.0 192.168.1.1" % (net_interface_type, riot_ip)
            else:
                # UNIX ifconfig command with sudo
                cmd = '"sudo ifconfig %s %s netmask 255.255.255.0"' % (net_interface_type, riot_ip)
                if "Linix" not in self.OS:
                    # request OSX root privilege with GUI promt
                    cmd = "osascript -e 'do shell script %s with prompt %s with administrator privileges'" % (cmd, '"ServerBIT requires root access."')
            print(">>> paste the following command: ")
            print ( cmd )
            return cmd

    def run_ifconfig_command(cmd):
        try:
            # wait unitl command has run before continuing
            proc = subprocess.check_output(cmd, shell=True)
            timer(3)
            return "ServerBIT R-IoT server is ready"
        except subprocess.CalledProcessError:
            return ("There was an error running this command. You can also change the ipv4 address manually (see R-IoT guide)  \
            \nclose window and try again")
            # sys.exit(1)

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
