pioneer_python_cli
==================

Barebones python command-line interface (cli) for controlling an internet-connected Pioneer AVR (Receiver/Amp).

Tested on a pioneer SC-1222-K.

Usage:

1. Find out your AVR's IP address.
2. Edit the telnet.py file, set the variable HOST to it, and do "python3 telnet.py <host>".

Some commands:
up   [volume up]
down [volume down]
mode [cycle through stereo and surround audio modes]
<input_name> [switch to given input]

Use control-D to exit.
