### WP edit
'''
requires python-osc and python3x
pip3 install python-osc
'''
from __main__ import asyncio
import json
from pythonosc import osc_message_builder
from pythonosc import osc_bundle_builder
from pythonosc import udp_client

from pythonosc import dispatcher, osc_server
from time import sleep

class OSC_Handler:
    device_name = "/bitalino"
    data_feature = "/raw/"
    output_address = ""
    labels = []

    BITalino_device = None
    is_recording = False
    wekaRecAddrStop = "/wekinator/control/stopRecording"
    wekaRecAddrStart = "/wekinator/control/startRecording"

    def __init__(self, ip, port, lbs, dev_id=0):
        self.client = udp_client.SimpleUDPClient(ip, port)
        self.labels = lbs
        # self.labels = ["nSeq", "I1", "I2", "O1", "O2","A1","A2","A3","A4","A5","A6"]
        self.dev_id = 0
        self.output_address = "/" + str(self.dev_id) + "/bitalino"

    # def init_server(self):
    #     def trigger_handler(args, name, *trigger_values):
    #         #pass output states
    #         led = 1 if trigger_values[0] > 0.5 else 0
    #         buzzer = 1 if trigger_values[1] > 0.5 else 0
    #         pwm_value = int(trigger_values[2])
    #         #select device (optional)
    #         id = 0 if len(trigger_values) < 4 else trigger_values[3]
    #         self.BITalino_device.trigger([led, buzzer])
    #         # self.BITalino_device[id].trigger([led, buzzer])
    #         # self.bq.put([name[0], value])
    #
    #     while self.BITalino_device is None:
    #         sleep(0.1)
    #     d = dispatcher.Dispatcher()
    #     d.map("/*/trigger", trigger_handler, 'triggers')
    #     self.server = osc_server.ThreadingOSCUDPServer(
    #           (self.ip, 12000), d)
    #     print("Trigger address: {}".format(self.server.server_address))
    #     self.server.serve_forever()

    async def sendTestBundle(self, numOutputs):
        bundle = osc_bundle_builder.OscBundleBuilder(
            osc_bundle_builder.IMMEDIATELY)
        msg = osc_message_builder.OscMessageBuilder(
            address=self.output_address)
        # Test bundle outputs: 1, 2, 3, ...
        testVal = 1.0
        for i in range(numOutputs):
            msg.add_arg(testVal)
            testVal = testVal + 1.0
        bundle.add_content(msg.build())
        bundle = bundle.build()
        self.client.send(bundle)

    # e.g '/<id>/bitalino/'
    async def output_bundle(self, data, whole_sequence=0):
        #printJSON(data)
        data = json.loads(data)
        while len(json.loads(json.dumps(data))) is 0:
            await asyncio.sleep(1.0)
        bundle = osc_bundle_builder.OscBundleBuilder(
            osc_bundle_builder.IMMEDIATELY)
        msg = osc_message_builder.OscMessageBuilder(
            address=self.output_address)
        for label, output_buffer in data.items():
            print (label + " " + str(output_buffer[0]))
            arg_to_add = output_buffer if whole_sequence == 1 else output_buffer[0]
            msg.add_arg(arg_to_add)
        bundle.add_content(msg.build())
        bundle = bundle.build()
        self.client.send(bundle)

    # e.g '/<id>/bitalino/A1'
    async def output_individual(self, data, whole_sequence=0):
        data = json.loads(data)
        #printJSON(data)
        bundle = osc_bundle_builder.OscBundleBuilder(
            osc_bundle_builder.IMMEDIATELY)

        for label in self.labels:
            self.output_address += self.device_number + "/bitalino/" + label
            msg = osc_message_builder.OscMessageBuilder(
                address=output_address)
            arg_to_add = data[label] if whole_sequence == 1 else data[label][0]
            msg.add_arg(arg_to_add)
            msg.build()
            self.client.send(msg)
        await asyncio.sleep(0.0)

def printJSON(decoded_json_input):
    try:
        # pretty printing of json-formatted string
        print (json.dumps(decoded_json_input, sort_keys=True , indent=4))
    except (ValueError, KeyError, TypeError):
        print ("JSON format error")
