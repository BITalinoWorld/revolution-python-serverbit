# Overview

ServerBIT (r)evolution is a barbone example application, which can be run like a service, designed to demonstrate the OpenSignals client-server architecture. You can use and modify the source code under the terms of the GPL licence.

This architecture uses the Tornado event-driven networking engine in an approach where a Python backend handles the connection to the device, and streams the acquired data in near real-time as JSON-formatted structures to a client over the WebSockets protocol.

Although this code is currently used for BITalino, it is completely general purpose.

`ServerBIT.py` connects to a device as per the configurations stored in a `config.json` file, expected to be found in the user home directory under a folder with the name `ServerBIT`. If it doesn't exist it is created automatically the first time the server is launched.

`ClientBIT.html` is an example HTML/JavaScript test client, which connects to ServerBIT and opens a connection to a specified BITalino device to acquire data from A1 (EMG data as of early-2014 units) and draw it on the browser in realtime.


## Pre-Configured Installers

- Can be downloaded and installed from: http://bitalino.com/en/development/utilities
- Already include a Python distribution with all the dependencies

### Windows

### Mac OS 

## Running from Sources

- Python 2.7 must be installed
- BITalino API and dependencies installed
- PySerial module installed
- Tornado module installed


## Testing ServerBIT

- Edit `config.json` on a text editor and change the `device` property to the MAC address or Virtual COM port of your BITalino device
- Launch the `ServerBIT.py` script using your Python interpreter
- Once a message similar to `LISTENING` appears in the console the server is ready to receive a connection
- Open `ClientBIT.html` on your web browser
- You should start to see the instruction call log on the page body, and a real time signal corresponding to A1


## References

H. Silva, A. Lourenço, A. Fred, R. Martins. BIT: Biosignal Igniter Toolkit. Computer Methods and Programs in Biomedicine, Volume 115, 2014, Pages 20-32.


M. Lucas da Silva, D. Gonçalves, T. Guerreiro, H. Silva. A Web-Based Application to Address Individual Interests of Children with Autism Spectrum Disorders. Procedia Computer Science, Volume 14, 2012, Pages 20-27.


