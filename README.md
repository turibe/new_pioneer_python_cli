# pioneer_python_cli

==================

Barebones Python command-line interface (CLI) for controlling an Internet-connected Pioneer AVR (Receiver/Amp).

Tested on a Pioneer SC-1222-K Amp.

License: MIT.

Disclaimer: *Use at your own risk.*

## Usage:

1. Find out your AVR's IP address.
2. Run "python3 telnet.py <ipaddress>".

## Some commands:

- `up`              [volume up]
- `down`            [volume down]
- `<integer>`       [if positive, increase volume this number of times, capped at 10]
- `-<integer>`      [if negative, decrease volume this number of times, capped at -30]

- `<input_name>`    [switch to given input]

- `mode X`          [choose audio modes; not all modes will be available]
- `mode help`       [help with modes]
- `surr`            [cycle through surround modes]
- `stereo`          [stereo mode]
- `status`          [print status]

- Use control-D to exit.
