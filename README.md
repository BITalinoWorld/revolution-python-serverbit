# OpenSignals Barebone

The ServerBIT (r)evolution is a barbone example application that can be run like a service, based on the Tornado event-driven networking engine, and designed to demonstrate the OpenSignals client-server architecture. You can use and modify the source code under the terms of the GPL licence.

This architecture is based on an asynchronous message passing protocol, in which the server and the client communicate using JSON-formatted strings. Although this code is primarily used for BITalino, it is completely general purpose.

`ServerBIT`.py connects to a device as per the configurations found in the `config.json` file and streams the data in real time over WebSockets.

`ClientBIT.html` is an example HTML/JS that connects to ServerBIT and opens a connection to a specified BITalino device to acquire data from A1 (EMG data as of early-2014 units) and draw it on the browser in realtime.


## Pre-configured Bundles

- Can be downloaded and installed from: http://bitalino.com/en/development/utilities 


## Running from Sources

- Python 2.7 or above must be installed;
- BITalino API and dependencies installed;
- PySerial module installed;
- Tornado module installed.


## Testing ServerBIT

- edit `config.json` on a text editor and change the `device` property to the MAC address or Virtual COM port of your BITalino device;
- launch the `ServerBIT.py` script using your Python interpreter;
- once a message similar to `LISTENING` appears in the console the server is ready to receive a connection;
- open `ClientBIT.html` on your web browser;
- you should start to see the instruction call log on the page body, and a real time signal corresponding to A1.


## References

H. Silva, A. Lourenço, A. Fred, R. Martins. BIT: Biosignal Igniter Toolkit. Computer Methods and Programs in Biomedicine, Volume 115, 2014, Pages 20-32.


M. Lucas da Silva, D. Gonçalves, T. Guerreiro, H. Silva. A Web-Based Application to Address Individual Interests of Children with Autism Spectrum Disorders. Procedia Computer Science, Volume 14, 2012, Pages 20-27.


