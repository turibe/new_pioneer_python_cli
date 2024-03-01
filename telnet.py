#!/usr/bin/python3

"""
Main script for controlling the AVR via telnet.
"""

import sys
import telnetlib
import urllib.parse
import threading
import argparse
import time

from typing import Optional

from modes_display import modeDisplayMap
from modes_set import modeSetMap, inverseModeSetMap



# HOST = "192.168.86.32"


inputMap = {
    "41" : "Pandora",
    "44" : "Media Server",
    "45" : "Favorites",
    "17" : "iPod/USB",
    "05" : "DVR",
    "01" : "TV",
    "13" : "USB-DAC",
    "02" : "TUNER",
    "00" : "PHONO",
    "12" : "MULTI CH IN",
    "33" : "ADAPTER PORT",
    "48" : "MHL",
    "31" : "HDMI" # cyclic
}

# a:str = inputMap.get("foo", None)

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

    # cycle through stereo modes:
    "stereo" : "0001SR",
    "unplugged" : "0109SR",
    "extended" : "0112SR",

    "mode" : "?S",

    "loud" : "9ATW", # cyclic

    # switch inputs:
    "bd" : "25FN",
    "dvd" : "04FN",
    "appleaudio" : "05FN",
    "amazontv" : "06FN",
    # "sat" : "06FN",
    "video" : "10FN",
    "hdmi1" : "19FN",
    "hdmi2" : "20FN",
    "hdmi3" : "21FN",
    "hdmi4" : "22FN",
    "hdmi5" : "23FN",
    "hdmi6" : "24FN",
    "apple" : "25FN",
    "appletv" : "25FN",
    "hdmi7" : "34FN",
    "net" : "26FN", # cyclic
    "tv" : "01FN",
    "iradio" : "38FN",
    "dvr" : "15FN",
    "radio" : "02FN",
    "tuner" : "02FN",
    "phono" : "00FN", # invalid command
    "hdmi" : "31FN", # cyclic
    "pandora" : "41FN",

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

    "info" : "?GAH",
    "list" : "?GAI",
    "top menu" : "19IP",

    # Tuner ones:
    "nextpreset" : "TPI",
    "prevpreset" : "TPD",
    "mpx" : "05TN",

}


def print_help():
    l = commandMap.keys()
    # l.sort()
    for x in l:
        print(x)
    print("mode [mode]")
    print(inverseModeSetMap.keys())

def send(tn, s:str):
    tn.write(s.encode() + b"\r\n")

def readline(tn) -> bytes:
    s = tn.read_until(b"\r\n")
    return s[:-2]

def decodeFL(s:str) -> Optional[str]:
    # print("Original Url string is:", s)
    if not s.startswith('FL'):
        return None
    s = s[2:] #  the FL
    s = s[2:] # skip first two
    i = 0
    url = ""
    while i < len(s):
        url += "%"
        url += s[i:i+2]
        i += 2
    result = urllib.parse.unquote(url)
    # print("Url is", url, "result is", result)
    return result

ErrorMap = {
    "E02" : "NOT AVAILABLE NOW",
    "E03" : "INVALID COMMAND",
    "E04" : "COMMAND ERROR",
    "E06" : "PARAMETER ERROR",
    "B00" : "BUSY"
    }

def parse_error(s:str):
    return ErrorMap.get(s, None)

def decodeAST(s:str) -> bool:
    if not s.startswith('AST'):
        return False
    s = s[3:]
    print("Audio input signal:" + decode_ais( s[0:2] ))
    print("Audio input frequency:" + decode_aif( s[2:4] ))
    # The manual starts counting at 1, so to fix this off-by-one, we do:
    s = '-' + s
    # channels...
    print("Input Channels:")
    if int(s[5]): print("Left, ")
    if int(s[6]): print("Center, ")
    if int(s[7]): print("Right, ")
    if int(s[8]): print("SL, ")
    if int(s[9]): print("SR, ")
    if int(s[10]): print("SBL, ")
    if int(s[11]): print("S, ")
    if int(s[12]): print("SBR, ")
    if int(s[13]): print("LFE, ")
    if int(s[14]): print("FHL, ")
    if int(s[15]): print("FHR, ")
    if int(s[16]): print("FWL, ")
    if int(s[17]): print("FWR, ")
    if int(s[18]): print("XL, ")
    if int(s[19]): print("XC, ")
    if int(s[20]): print("XR, ")
    print("")
    print("Output Channels:")
    if int(s[26]): print("Left, ")
    if int(s[27]): print("Center, ")
    if int(s[28]): print("Right, ")
    if int(s[29]): print("SL, ")
    if int(s[30]): print("SR, ")
    if int(s[31]): print("SBL, ")
    if int(s[32]): print("S, ")
    if int(s[33]): print("SBR, ")
    if int(s[34]): print("LFE, ")
    if int(s[35]): print("FHL, ")
    if int(s[36]): print("FHR, ")
    if int(s[37]): print("FWL, ")
    if int(s[38]): print("FWR, ")
    print("")
    sys.stdout.flush()
    return True

# def decode_vst(s:str) -> bool:
#     if not s.startswith("VST"):
#         return False
#     s = s[3:]
#     s = '=' + s
#     return True

def decode_aif(s:str) -> str:
    if s=="00": return "32kHz"
    if s=="01": return "44.1kHz"
    if s=="02": return "48kHz"
    if s=="03": return "88.2kHz"
    if s=="04": return "96kHz"
    if s=="05": return "176.4kHz"
    if s=="06": return "192kHz"
    if s=="07": return "---"
    return "unknown"

def decode_ais(s:str) -> str:
    if "00" <= s <= "02": return "ANALOG"
    if s=="03" or s=="04": return "PCM"
    if s=="05": return "DOLBY DIGITAL"
    if s=="06": return "DTS"
    if s=="07": return "DTS-ES Matrix"
    if s=="08": return "DTS-ES Discrete"
    if s=="09": return "DTS 96/24"
    if s=="10": return "DTS 96/24 ES Matrix"
    if s=="11": return "DTS 96/24 ES Discrete"
    if s=="12": return "MPEG-2 AAC"
    if s=="13": return "WMA9 Pro"
    if s=="14": return "DSD->PCM"
    if s=="15": return "HDMI THROUGH"
    if s=="16": return "DOLBY DIGITAL PLUS"
    if s=="17": return "DOLBY TrueHD"
    if s=="18": return "DTS EXPRESS"
    if s=="19": return "DTS-HD Master Audio"
    if "20" <= s <= "26": return "DTS-HD High Resolution"
    if s=="27": return "DTS-HD Master Audio"
    return "unknown"

def db_level(s) -> str:
    n = int(s)
    db = 6 - n
    return f"{db}dB"

def decode_tone(s: str) -> Optional[str]:
    if s.startswith("TR"):
        return "treble at " + db_level(s[2:4])
    if s.startswith("BA"):
        return "bass at " + db_level(s[2:4])
    if s == "TO0":
        return "tone off"
    if s == "TO1":
        return "tone on"
    return None

sourceMap = {
    "00" : "Intenet Radio",
    "01" : "Media Server",
    "06" : "SiriusXM",
    "07" : "Pandora",
    "10" : "AirPlay",
    "11" : "Digital Media Renderer (DMR)"
}

typeMap = {
    "20" : "Track",
    "21" : "Artist",
    "22" : "Album",
    "23" : "Time",
    "24" : "Genre",
    "25" : "Chapter Number",
    "26" : "Format",
    "27" : "Bitrate",
    "28" : "Category",
    "29" : "Composer1",
    "30" : "Composer2",
    "31" : "Buffer",
    "32" : "Channel"
}

screenTypeMap = {
    "00" : "Message",
    "01" : "List",
    "02" : "Playing (Play)",
    "03" : "Playing (Pause)",
    "04" : "Playing (Fwd)",
    "05" : "Playing (Rev)",
    "06" : "Playing (Stop)",
    "99" : "Invalid"
}


def decodeGeh(s: str) -> Optional[str]:
    if s.startswith("GDH"):
        bytes = s[3:]
        return "items " + bytes[0:5] + " to " + bytes[5:10] + " of total " + bytes[10:]
    if s.startswith("GBH"):
        return "max list number: " + s[2:]
    if s.startswith("GCH"):
        return screenTypeMap.get(s[3:5], "unknown")  + " - " + s
    if s.startswith('GHH'):
        source = s[2:]
        return "source: " + sourceMap.get(source, "unknown")
    if not s.startswith('GEH'):
        return None
    s = s[3:]
    # line = s[0:2]
    # focus = s[2]
    tstring = s[3:5]
    typeval = typeMap.get(tstring, f"unknown ({tstring})")
    info = s[5:]
    return typeval + ": " + info


# We really want two threads: one with the output, another with the commands.

def read_loop(tn: telnetlib.Telnet) -> None:
    """Main read loop"""
    sys.stdout.flush()
    count:int = 0
    while True:
        count += 1
        b:bytes = readline(tn)
        s = b.decode()
        err = parse_error(s)
        if err:
            print(count, "ERROR: ", err)
            continue
        tone = decode_tone(s)
        if tone:
            print(tone)
            continue
        geh = decodeGeh(s)
        if geh:
            print(geh)
            continue
        # print("s has type", type(s)) # bytes
        fl = decodeFL(s)
        if fl:
            sys.stdout.write(f"{fl}\r")
            continue
        if s.startswith('FN'):
            inputs = inputMap.get(s[2:], f"unknown ({s})")
            print(f"Input is {inputs}")
            continue
        if s.startswith('ATW'):
            print("loudness is ")
            print("on" if s == "ATW1" else "off")
            continue
        if s.startswith('ATC'):
            print("eq is ")
            print("on" if s == "ATC1" else "off")
            continue
        if s.startswith('ATD'):
            print("standing wave is ")
            print("on" if s == "ATD1" else "off")
            continue
        if s.startswith('ATE'):
            num = s[3:]
            if "00" <= num <= "16":
                print("Phase control: " + num + "ms")
            else:
                if num == "97":
                    print("Phase control: AUTO")
                elif num == "98":
                    print("Phase control: UP")
                elif num == "99":
                    print("Phase control: DOWN")
                else:
                    print("Phase control: unknown")
            continue
        m = translate_mode(s)
        if m:
            print(f"Listening mode is {m} ({s})")
            continue
        if s.startswith('AST') and decodeAST(s):
            continue
        if s.startswith('SR'):
            code = s[2:]
            v = modeSetMap.get(code, None)
            if v:
                print(f"mode is {v} ({s})")
                continue
        # default:
        print(count, s)


def write_loop(tn: telnetlib.Telnet) -> None:
    """Main write loop"""
    s: Optional[str] = None
    while True:
        command = input("command: ").strip()
        if command in ("quit", "exit"):
            print("Read thread says bye-bye!")
            # sys.exit()
            return
        if command == "status":
            get_status(tn)
            continue
        if command in ("help", "?"):
            print_help()
            continue
        if command.startswith("select"):
            s = second_arg(command).rjust(2,"0") + "GFI"
            send(tn, s)
            continue
        if command.startswith("display"):
            s = second_arg(command).rjust(5, "0") + "GCI" # may need to pad with zeros.
            send(tn, s)
            continue
        intval = int(command) if command.split("-", 1)[-1].isdecimal() else None
        if intval:
            if intval > 0:
                intval = max(intval, 5)
                for x in range(1,intval,1):
                    send(tn, "VU")
                    time.sleep(0.1)
            if intval < 0:
                intval = abs(max(intval, -30))
                for x in range(0,intval,1):
                    send(tn, "VD")
                    time.sleep(0.1)
            continue
        s = commandMap.get(command, None)
        if s:
            send(tn, s)
            continue
        if command.startswith("mode"):
            change_mode(tn, command)
            continue
        if command != "":
            print("Sending raw command " + command)
            sys.stdout.flush()
            send(tn, command) # try original one


# TODO: some modes work and some don't
# document which ones, only include those in help

def change_mode(tn, command:str) -> bool:
    l = command.split(" ")
    if len(l) < 2:
        return False
    modestring = " ".join(l[1:]).lower()
    m = inverseModeSetMap.get(modestring, None)
    if m:
        send(tn, m + "SR")
        return False
    print("Unknown " + command) # "Unknown mode <mode>" message
    return False

def second_arg(cmd: str) -> str:
    l = cmd.split(" ")
    if len(l) < 2:
        return ""
    return l[1].strip()

# Listening mode, in the order they appear in the spreadsheet.
# looks like PDF doc has different ones (it's from 2010)
# These come from the list of listening mode requests, which is shorter than
# the list of displayed modes (above)

def translate_mode(s: str) -> Optional[str]:
    if not s.startswith('LM'):
        return None
    s = s[2:]
    m = modeDisplayMap.get(s, None)
    return m or "Unknown"


def get_status(tn):
    """Gets the status by sending a series of status requests.
       Each request prints the corresponding info."""
    send(tn, "?BA")
    send(tn, "?TR")
    send(tn, "?TO")
    send(tn, "?L")
    send(tn, "?AST")


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

    telnet_connection = telnetlib.Telnet(args.host)
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
