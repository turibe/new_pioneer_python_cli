pioneer_python_cli
==================

Barebones python command-line interface (cli) for controlling an internet-connected Pioneer AVR (Receiver/Amp).

Tested on a pioneer SC-1222-K.

** Usage:

1. Find out your AVR's IP address.
2. Edit the telnet.py file, set the variable HOST to it, and do "python3 telnet.py <host>".

** Some commands:

up              [volume up]
down            [volume down]
<integer>       [if positive, increase volume this number of times, max 5]
-<integer>      [if negative, decrease volume this number of times]

<input_name>    [switch to given input]
mode            [cycle through stereo and surround audio modes]
status          [print status]

Use control-D to exit.
