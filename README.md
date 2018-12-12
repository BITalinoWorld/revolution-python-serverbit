# Overview

ServerBIT (r)evolution is a minimal software package inteded to support Rapid Application Development. This is designed to demonstrate the OpenSignals client-server architecture. You can use and modify the source code under the terms of the GPL licence.

This architecture uses the Tornado event-driven networking engine in an approach where a Python backend handles the connection to the device, and streams the acquired data in near real-time as JSON-formatted structures to a client over the WebSockets or OSC protocol. This can be used as a service to communicate to other applications and devices (see [Examples](#Examples))

The lastest update icludes the following features:

- Python 3 support
- Web configuration interface with device finder
- [R-IoT](http://bitalino.com/en/r-iot-kit) support
- Multiple device managment
- Open Sound Control (OSC) output
- Trigger actuation events from Web or OSC messages

To access the barebones version of ServerBIT, please see [this repository](https://github.com/BITalinoWorld/revolution-python-serverbit)

`ServerBIT.py` connects to a device as per the configurations stored in a `config.json` file, expected to be found in the user home directory under a folder with the name `ServerBIT`. If it doesn't exist it is created automatically the first time the server is launched.

`ClientBIT.html` is an example HTML/JavaScript test client, which connects to ServerBIT and opens a connection to a specified BITalino device to acquire data from A1 (EMG data as of early-2014 units) and draw it on the browser in realtime. See [Examples](#Examples) for more use cases

`config.html` can be accessed once ServerBIT has been launched, where you are able to set the default ServerBIT configuraton.

# Pre-Configured Installers

We have prepared user-friendly installers that already include a Python distribution with all the dependencies. The following instructions should guide you through the initial steps needed to reach a viable and repeatable configuration. For illustrative purposes, let's consider that the MAC address of your device is `01:23:45:67:89:AB`

## Windows

- Download and install ServerBIT: http://www.bitalino.com/downloads/ServerBIT_win64.zip
- Launch ServerBIT
- Go the configuratoin page on your browser `localhost:9001/config`
- In the device finder, select Bluetooth and/or OSC and proceed to `Find Devices`, a loading icon should appear
- When complete, select a device address in the dropdown menu below and click `Update Device List`. The address should appear under Device List like so `["01:23:45:67:89:AB"]`
- Continue through the configuration page and click `Submit` to save
- From now on whenever you execute the ServerBIT_Launcher app it should automatically connect to your device(s) and continuously stream data
- A configuration test can be made using the `ClientBIT.html` page found on the `ServerBIT` directory on your home folder
- When finished, Close the command line window to exit ServerBIT

## Mac OS

- Download and install ServerBIT: http://www.bitalino.com/downloads/ServerBIT.pkg
- Launch ServerBIT
- The ServerBIT icon should appear in the menu bar. Click the icon, then `Preferences` to go the configuratoin page on your browser `localhost:9001/config` (or enter the address manually)
- In the device finder, select Bluetooth and/or OSC and proceed to `Find Devices`, a loading icon should appear
- When complete, select a device address in the dropdown menu below and click `Update Device List`. The address should appear under Device List like so `["/dev/tty.BITalino-89-AB-DevB"]`
- Continue through the configuration page and click `Submit` to save
- From now on whenever you execute the ServerBIT_Launcher app it should automatically connect to your device(s) and continuously stream data
- A configuration test can be made using the `ClientBIT.html` page found on the `ServerBIT` directory on your home folder
- When finished, go to the ServerBIT toolbar icon and  click `close`

# Examples
Software templates for Websockets and OSC communication will be added to this repository:
https://gitlab.com/weselle/serverbit-examples

# Running from Sources

## Dependencies

#####  Any OS

- Python 3.6+ must be installed
- BITalino API and dependencies installed
- PySerial module installed
- Tornado module installed

#####  OSX

- To enable the status bar app, install [rumps](https://github.com/jaredks/rumps)
- You can then launch/restart ServerBIT using the following command
```
./start_mac.sh
```

#####  LINUX

If connecting a R-IoT module using *linux* you'll need to install gksudo
```
sudo apt-get install gksu
```
- You can then launch/restart ServerBIT using the following command
```
./start_linux.sh
```

## Testing ServerBIT

- Launch the `start_<OS>` shell or bash script from the command line to create `ServerBIT` directory on your home folder and `config.json` file.
- Go the configuratoin page on your browser `localhost:9001/config`
- In the device finder, select Bluetooth and/or OSC and proceed to `Find Devices`, a loading icon should appear
- When complete, select a device address in the dropdown menu below and click `Update Device List`. The address should appear under Device List like so `["01:23:45:67:89:AB"]`
- Continue through the configuration page and click `Submit` to save
- Re-launch ServerBIT
- Once a message similar to `LISTENING` appears in the console the server is ready to receive a connection
- Open `ClientBIT.html` on your web browser
- You should start to see the instruction call log on the page body and a real time signal corresponding to A1 on `ClientBIT.html`


# Settings in `config.json`
Whilst it's recommended to only use the config page to change any settings, it's possible to manually edit the config file created in the home directory.

- `"device"`: MAC address or Virtual COM port (VCP) of your BITalino device(s). Multiple devices can be set using an array e.g *"device": ["01:23:45:67:89:AB", "/0/raw"]*
- `"channels"`: List of channels to be acquired from the device (e.g. [1, 6] acquires channels A1 and A6)
- `"sampling_rate"`: Sampling rate at which data should be acquired (i.e. 1000, 100, 10 or 1 Hz)
- `buffer_size`: Number of elements in each output sequence (BITalino only)
- `ip_address`: Address through which ServerBIT will be streaming data. Set to *localhost* by default
- `"port"`: Port through which ServerBIT will be streaming data (applies to OSC and Websockets)
- `"labels"`: Human-readable descriptor associated with each channel acquired by the device, and that will be used to name the properties on the JSON-formatted structure created for streaming (**NOTE:** BITalino always sends a sequence number, two digital inputs and two digital outputs, hence the 5 first entries in the `"labels"` array)
- `OSC_config`: Defaults for connecting the R-IoT module via OSC. Includes IP, Port, ssid and network_interface

*If there is an error in the config, use `Reset Config` on the web interface to restore to defaults*

# R-IoT Configuration
ServerBIT can be used to reconfigure your network settings to receive OSC data assuming the default configuration of the R-IoT. If you are using an alternative setup, please change the `OSC_config` values in `config.json` to match

- Enable Wi-Fi and launch ServerBIT
- Got to the configuration page
- Select `OSC(R-IoT)` in `Device Finder`
- If a terminal command is generated, proceed to `Run Command` (or copy and excecute into your terminal). You may need to allow administrator access to make changes
- When you receive the message *ServerBIT R-IoT Server is ready* process to `Find Devices`
- Select your device from the device dropdown. This should appear in the format `/<id>/raw`

For a barebones terminal-based bridge, try [riot-serverbit](https://gitlab.com/weselle/riot-serverbit)

#### Getting back online
As ServerBIT will change your static IP address, you may need to reset your network settings to get back online. Excecute the OS-appropriate shell script to do so:

**OSX***
```
./reset_net_config.sh
```
**Windows***
```
reset_net_config.vb
```

# OSC message reference

OSC messages can be used to listen for sensor data and manage actuation for each device connected.

Each device is assigned an id number, which can be used to identify individual modules. The device `<id>` will be **0** if only using a single device

### Data streaming

By default, data will be streamed as separate arrays according to the labels and channels selected. In this case, the output adress format is:

```
address: /<id>/bitalino
```

To have all the device data sent with the same message address, check `consolidate_outputs`
```
address: /all/bitalino
```

**Note: ** Some OSC listeners require an expected number of inputs. Make sure this matches the number of selected channels, acknowledging that BITalino always sends a sequence number, two digital inputs and two digital outputs. These are marked as:
`"nSeq", "I1", "I2", "O1", "O2"`

The OSC output message can be found on the config page
[(example)](/uploads/ce8d01ba42238fc47920330020458927/Screen_Shot_2018-11-28_at_11.31.24_AM.png)

### Trigger messages

Trigger messages can be used to manage actuation from the device's output channels. For the BITalino use this message format followed by an array of 3 float values:

```
address: /<id>/trigger
message: [O1, O2, pwd]
```

# Troubleshooting

- Verify that your device is turned on... its one of the most common cause of problems :D
- Be sure that either Bluetooth or Wi-Fi are enabled on your computer
- Double check the `config.json` to confirm that the MAC address or Virtual COM port (VCP) of your BITalino device is correct and correctly formatted
- Make sure that the port listed on the `config.json` file matches the one on your client
- Depending on how you are accessing the server, confirm that the client is connecting to the correct IP address
- If your home folder has non-standard ASCII characters modifications to the ServerBIT source code may be needed
- Launch the `ServerBIT.py` script using a Python interpreter to obtain additional information about the error
- Post an issue in this repository and we'll try to support to the best of our abilities

# References

H. Silva, A. Lourenço, A. Fred, R. Martins. BIT: Biosignal Igniter Toolkit. Computer Methods and Programs in Biomedicine, Volume 115, 2014, Pages 20-32.


M. Lucas da Silva, D. Gonçalves, T. Guerreiro, H. Silva. A Web-Based Application to Address Individual Interests of Children with Autism Spectrum Disorders. Procedia Computer Science, Volume 14, 2012, Pages 20-27.
