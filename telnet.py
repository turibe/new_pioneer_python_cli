#!/usr/bin/python3

"""
Main script for controlling the AVR via telnet.
"""

import sys
import telnetlib

import threading
import argparse
import time

from typing import Optional

from modes_display import modeDisplayMap
from modes_set import modeSetMap, inverseModeSetMap

import sources
import decoders

import config
report = config.report
print_lock = config.print_lock

# HOST = "192.168.86.32"

commandMap = {
    "on" : "PO",
    "off": "PF",
    "up": "VU",
    "+": "VU",
    "down": "VD",
    "-": "VD",
    "mute": "MO",
    "unmute": "MF",

    "volume": "?V",

    "tone" : "9TO", # cyclic
    "tone off" : "0TO",
    "tone on" : "1TO",
    "treble up" : "TI",
    "treble down" : "TD",
    "treble reset" : "06TR",
    "bass up" : "BI",
    "bass down" : "BD",
    "bass reset" : "06BA",

    "mcacc" : "MC0", # cyclic

    # phase control is recommended to be on:
    "phase" : "IS9", # cyclic

    "stereo" : "0001SR", # cycle through stereo modes
    "unplugged" : "0109SR",
    "extended" : "0112SR",

    "mode" : "?S",
    "model" : "?RGD",
    "mac address" : "?SVB",
    "software version" : "?SSI",

    "loud" : "9ATW", # cyclic

    # commands for switching inputs have the form XXFN, now derived from inputSourcesMap.
    # "phono" : "00FN", # invalid command
    # "hdmi" : "31FN", # cyclic

    # TODO: could have a pandora mode, radio mode, etc.
    # Pandora ones:
    "start" : "30NW",
    "next" : "13NW",
    "pause" : "11NW",
    "play" : "10NW",
    "previous" : "12NW",
    "stop" : "20NW",
    "clear" : "33NW",
    "repeat" : "34NW",
    "random" : "35NW",
    "menu" : "36NW",

    "netinfo" : "?GAH",
    "list" : "?GAI",
    "top menu" : "19IP",

    # Tuner ones:
    "nextpreset" : "TPI",
    "prevpreset" : "TPD",
    "mpx" : "05TN",

    # Cyclic mode shortcuts:
    # cycles through thx modes, but input must be THX:
    "thx" : "0050SR",
    # cycles through surround modes (shortcut for "mode" command):
    "surr" : "0100SR",

    "video status" : "?VST"
}

def print_help():
    "Prints help for the main commands"
    l = commandMap.keys()
    # l.sort()
    for x in l:
        print(x)
    print("""Use "help mode" for information on modes, "help sources" for changing input sources, "quit" to exit\n""")

def print_mode_help():
    "Lists the mode change options (not all work)"
    print("mode [mode]\tfor one of:\n")
    for i in inverseModeSetMap:
        print(f"{i}")

def print_input_source_help():
    "Lists the input source change commands"
    print("Enter one of the following to change input:")
    for (i,inv) in sorted(SOURCE_MAP.inverse_map.items()):
        print(f"{i} ({inv})")
    print("Use 'learn' to update this map, 'save' to save it.")

def send(tn, s:str):
    "Sends the given string as bytes"
    tn.write(s.encode() + b"\r\n")

def readline(tn) -> bytes:
    "Reads a line from the connection"
    s = tn.read_until(b"\r\n")
    return s[:-2]


ErrorMap = {
    "E02" : "NOT AVAILABLE NOW",
    "E03" : "INVALID COMMAND",
    "E04" : "COMMAND ERROR",
    "E06" : "PARAMETER ERROR",
    "B00" : "BUSY"
    }

def parse_error(s:str):
    """Looks up error code that comes back from AVR"""
    return ErrorMap.get(s, None)

SOURCE_MAP = sources.SourceMap()
SOURCE_MAP.read_from_file()

# We really want two threads: one with the output, another with the commands.

def read_loop(tn: telnetlib.Telnet) -> None:
    """Main loop that reads and decodes data that comes back from the AVR"""
    sys.stdout.flush()
    count:int = 0
    while True:
        count += 1
        b:bytes = readline(tn)
        s = b.decode().strip()
        err = parse_error(s)
        if err:
            report(f"ERROR: {err}")
            continue
        if s.startswith("RGB"):
            # report(f"Learning (maybe) from '{s[3:]}'") # only if new
            SOURCE_MAP.learn_input_from(s[3:])
            continue
        if decoded := decoders.try_all(s):
            report(decoded)
            continue
        if s == "PWR0":
            report("Power is ON")
            continue
        if s == "PWR1":
            report("Power is OFF")
            continue
        if s.startswith("SVB"):
            report(f"AVR mac address: {s[3:]}\n")
            continue
        if s.startswith("SSI"):
            report(f"AVR software version: {s[3:]}\n")
            continue
        if s.startswith('FN'):
            inputs = SOURCE_MAP.get(s[2:], f"unknown ({s})")
            report(f"Input is {inputs}\n")
            continue
        if s.startswith('ATW'):
            flag = "on" if s == "ATW1" else "off"
            report(f"loudness is {flag}\n")
            continue
        if s.startswith('ATC'):
            fl = "on" if s == "ATC1" else "off"
            report(f"eq is {fl}\n")
            continue
        if s.startswith('ATD'):
            fl = "on" if s == "ATD1" else "off"
            report(f"standing wave is {fl}\n")
            continue
        if m := translate_mode(s):
            report(f"Listening mode is {m} ({s})")
            continue
        if s.startswith('SR'):
            code = s[2:]
            v = modeSetMap.get(code, None)
            if v:
                report(f"mode is {v} ({s})")
                continue
        if s.startswith('VOL'):
            continue
        # default:
        if len(s) > 0:
            report(f"Unknown status line {s}")


def write_loop(tn: telnetlib.Telnet) -> None:
    """Main loop that reads user input and sends commands to the AVR"""
    s: Optional[str] = None
    while True:
        try:
            read = input("command: ")
        except  EOFError:
            print("Goodbye!")
            sys.exit(0)
        command = read.strip()
        split_command = command.split()
        base_command = split_command[0] if len(split_command) > 0 else None
        second_arg = split_command[1] if len(split_command) > 1 else None
        # print(f"base command: {base_command}\n")
        if command in ("quit", "exit"):
            print("Read thread says bye-bye!")
            # sys.exit()
            return
        if command == "debug":
            config.DEBUG = not config.DEBUG
            report(f"Debug is now {config.DEBUG}")
            continue
        if command == "status":
            get_status(tn)
            continue
        if command == "learn":
            # query the range of source codes to get their names back (if any):
            for i in range(0,60):
                s = str(i).rjust(2,"0")
                send(tn, f"?RGB{s}")
            continue
        if command == "save":
            SOURCE_MAP.save_to_file()
            continue
        if command == "sources" or command == "inputs":
            with print_lock:
                print_input_source_help()
            continue
        if command == "modes":
            with print_lock:
                print_mode_help()
            continue
        if base_command in ("help", "?"):
            if command in ("help", "?"):
                with print_lock:
                    print_help()
                continue
            if len(split_command) > 1 and split_command[1] in ["mode", "modes"]:
                with print_lock:
                    print_mode_help()
                continue
            if len(split_command) > 1 and ("inputs".startswith(split_command[1]) or "sources".startswith(split_command[1])):
                print_input_source_help()
                continue
            report(f"""Couldn't recognize help command "{command}" """)
            continue
        # to select from a menu:
        if base_command == "select" and second_arg:
            s = second_arg.rjust(2,"0") + "GFI"
            send(tn, s)
            continue
        # to display from a menu:
        if base_command == "display" and second_arg:
            s = second_arg.rjust(5, "0") + "GCI" # may need to pad with zeros.
            send(tn, s)
            continue
        # check if command is just a positive or negative integer:
        intval = int(command) if command.split("-", 1)[-1].isdecimal() else None
        if intval:
            if intval > 0:
                intval = min(intval, 10)
                report(f"Volume up {intval}")
                for _x in range(0, intval):
                    send(tn, "VU")
                    time.sleep(0.1)
            if intval < 0:
                intval = abs(max(intval, -30))
                report(f"Volume down {intval}")
                for _x in range(0, intval):
                    send(tn, "VD")
                    time.sleep(0.1)
            continue
        s = commandMap.get(command, None) or SOURCE_MAP.inverse_map.get(command, None) # changing to a source by using the source name as the command
        if s:
            send(tn, s)
            continue
        if base_command == "mode":
            change_mode(tn, split_command)
            continue
        if command != "":
            report(f"Sending raw command {command}")
            sys.stdout.flush()
            send(tn, command) # try raw command


# TODO: some modes work and some don't;
# document which ones, only include those in help

def get_modes_with_prefix(prefix:str) -> set[str]:
    """Returns all the map keys that start with prefix --- except when prefix
    is itself a key, in that case, only preix is returned"""
    if inverseModeSetMap.get(prefix, None) is not None:
        return [prefix]
    s:set[str] = set({})
    for i in inverseModeSetMap:
        if i.startswith(prefix):
            s.add(i)
    return s

# return value not used:
def change_mode(tn, l: list[str]) -> bool:
    "Attempts to change the mode given the (split) command l"
    if len(l) < 2:
        return False
    modestring = " ".join(l[1:]).lower()
    if modestring == "help":
        print_mode_help()
        return False
    mset = get_modes_with_prefix(modestring)
    if len(mset) == 0:
        report(f"Unknown mode {modestring}") # "Unknown mode <mode>" message
        return False
    if len(mset) == 1:
        mode = mset.pop()
        m = inverseModeSetMap.get(mode)
        assert m is not None
        report(f"trying to change mode to {modestring} ({m})")
        send(tn, m + "SR")
        return False
    with print_lock:
        print("Which one do you mean? Options are:")
        for i in mset:
            print(i)
    return False

def second_arg_fun(cmd: str) -> Optional[str]:
    """second argument, if any"""
    l = cmd.split(" ")
    if len(l) < 2:
        return None
    return l[1].strip()

# Listening mode, in the order they appear in the spreadsheet.
# looks like PDF doc has different ones (it's from 2010)
# These come from the list of listening mode requests, which is shorter than
# the list of displayed modes (above)

def translate_mode(s: str) -> Optional[str]:
    if not s.startswith('LM'):
        return None
    s = s[2:]
    return modeDisplayMap.get(s, "Unknown")


def get_status(tn: telnetlib.Telnet):
    """Gets the status by sending a series of status requests.
       Each request prints the corresponding info."""
    send(tn, "?P") # power
    send(tn, "?F") # input
    send(tn, "?BA")
    send(tn, "?TR")
    send(tn, "?TO")
    send(tn, "?L")
    send(tn, "?AST")
    send(tn, "?IS")
    send(tn, "?VST")
    # send(tn, "?VTC") # not very interesting if always AUTO


class ReadThread(threading.Thread):
    """ This thread reads the lines coming back from telnet """
    def __init__(self, tn):
        self.tn = tn
        threading.Thread.__init__(self)
    def run(self):
        read_loop(self.tn)


# TODO: add command-line options to control, for example, displaying the info from the screen;
# also, for one-off commands.

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('host', metavar='host', type=str, help='address of AVR')

    args = parser.parse_args()
    print(f"AVR hostname/address is {args.host}")

    telnet_connection = telnetlib.Telnet(args.host, port=23)
    # telnet_connection.set_debuglevel(100)
    # time.sleep(0.5)

    test_s = telnet_connection.read_very_eager()
    # print("very eager: ", test_s)

    send(telnet_connection, "?P") # to wake up

    readThread = ReadThread(telnet_connection)
    readThread.daemon = True
    readThread.start()

    # the main thread does the writing, and everything exits when it does:
    write_loop(telnet_connection)
