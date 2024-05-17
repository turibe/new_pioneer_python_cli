
from typing import Optional

import config
report = config.report

# TODO: add unit tests

def decode_fl(s:str) -> Optional[str]:
    # print("Original Url string is:", s)
    if not s.startswith('FL'):
        return None
    s = s[2:] # the FL
    s = s[2:] # skip first two
    result = bytes.fromhex(s).decode('ascii')
    # print("original is", s, "result is", result)
    return result


def decode_geh(s: str) -> Optional[str]:
    if s.startswith("GDH"):
        sbytes = s[3:]
        return "items " + sbytes[0:5] + " to " + sbytes[5:10] + " of total " + sbytes[10:]
    if s.startswith("GBH"):
        return "max list number: " + s[2:]
    if s.startswith("GCH"):
        return screenTypeMap.get(s[3:5], "unknown")  + " - " + s
    if s.startswith('GHH'):
        source = s[2:]
        return "source: " + internetSourceMap.get(source, "unknown")
    if not s.startswith('GEH'):
        return None
    s = s[3:]
    # line = s[0:2]
    # focus = s[2]
    tstring = s[3:5]
    typeval = trackFieldsMap.get(tstring, f"unknown ({tstring})")
    info = s[5:]
    return typeval + ": " + info

internetSourceMap = {
    "00" : "Intenet Radio",
    "01" : "Media Server",
    "06" : "SiriusXM",
    "07" : "Pandora",
    "10" : "AirPlay",
    "11" : "Digital Media Renderer (DMR)"
}

trackFieldsMap = {
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


VTC_resolution_map = {
    "00": "AUTO Resolution",
    "01": "PURE Resolution",
    "02": "Reserved Resolution",
    "03": "R480/576 Resolution",
    "04": "720p Resolution",
    "05": "1080i Resolution",
    "06": "1080p Resolution",
    "07": "1080/24p Resolution"
    }

def decode_vtc(s: str) -> bool:
    "Decodes a VTC (video resolution) status status string"
    assert s.startswith('VTC')
    s = s[3:]
    print(VTC_resolution_map.get(s, "unknown VTC resolution"))
    return True


CHANNEL_MAP = {
    5: "Left",
    6: "Center",
    7: "Right",
    8: "SL",
    9: "SR",
    10: "SBL",
    11: "S",
    12: "SBR",
    13: "LFE",
    14: "FHL",
    15: "FHR",
    16: "FWL",
    17: "FWR",
    18: "XL",
    19: "XC",
    20: "XR"
}

def decode_ast(s:str) -> bool:
    "Decodes an AST return status string"
    assert s.startswith('AST')
    s = s[3:]
    print("Audio input signal: " + decode_ais( s[0:2] ))
    print("Audio input frequency: " + decode_aif( s[2:4] ))
    # The manual starts counting at 1, so to fix this off-by-one, we do:
    s = '-' + s
    # channels...
    print("Input Channels:")
    for (i,v) in sorted(CHANNEL_MAP.items()):
        if i >= len(s):
            break
        if int(s[i]):
            print(f"{v}, ")
    print("")
    print("Output Channels:")
    for (i,v) in sorted(CHANNEL_MAP.items()):
        idx = i + 21
        if idx >= len(s):
            break
        if int(s[idx]):
            print(f"{v}, ")
    print("")
    return True


aif_map = {
    "00": "32kHz",
    "01": "44.1kHz",
    "02": "48kHz",
    "03": "88.2kHz",
    "04": "96kHz",
    "05": "176.4kHz",
    "06":  "192kHz",
    "07": "---"
}


def decode_aif(s:str) -> str:
    return aif_map.get(s, "unknown")

def decode_ais(s:str) -> str:
    if "00" <= s <= "02":
        return "ANALOG"
    if s=="03" or s=="04":
        return "PCM"
    if s=="05":
        return "DOLBY DIGITAL"
    if s=="06":
        return "DTS"
    if s=="07":
        return "DTS-ES Matrix"
    if s=="08":
        return "DTS-ES Discrete"
    if s=="09":
        return "DTS 96/24"
    if s=="10":
        return "DTS 96/24 ES Matrix"
    if s=="11":
        return "DTS 96/24 ES Discrete"
    if s=="12":
        return "MPEG-2 AAC"
    if s=="13":
        return "WMA9 Pro"
    if s=="14":
        return "DSD->PCM"
    if s=="15":
        return "HDMI THROUGH"
    if s=="16":
        return "DOLBY DIGITAL PLUS"
    if s=="17":
        return "DOLBY TrueHD"
    if s=="18":
        return "DTS EXPRESS"
    if s=="19":
        return "DTS-HD Master Audio"
    if "20" <= s <= "26":
        return "DTS-HD High Resolution"
    if s=="27":
        return "DTS-HD Master Audio"
    return "unknown"

def db_level(s:str) -> str:
    "db level conversion"
    n = int(s)
    db = 6 - n
    return f"{db}dB"

def decode_tone(s: str) -> Optional[str]:
    "readable version of the tone status"
    if s.startswith("TR"):
        return "treble at " + db_level(s[2:4])
    if s.startswith("BA"):
        return "bass at " + db_level(s[2:4])
    if s == "TO0":
        return "tone off"
    if s == "TO1":
        return "tone on"
    return None

SIGNAL_MAP = {
    "0": "---",
    "1": "VIDEO",
    "2": "S-VIDEO",
    "3": "COMPONENT",
    "4": "HDMI",
    "5": "Self OSD/JPEG"
    }

SIGNAL_FORMAT_MAP = {
    "00": "---",
    "01": "480/60i",
    "02": "576/50i",
    "03": "480/60p",
    "04": "576/50p",
    "05": "720/60p",									
    "06": "720/50p",
    "07": "1080/60i",    
    "08": "1080/50i",
    "09": "1080/60p",
    "10": "1080/50p",									
    "11": "1080/24p",    
    "12": "4Kx2K/24Hz",
    "13": "4Kx2K/25Hz",
    "14": "4Kx2K/30Hz",
    "15": "4Kx2K/24Hz(SMPTE)"
    }

ASPECT_MAP = {
    "0": "---",
    "1": "4:3",
    "2": "16:9",
    "3": "14:9"
    }

# HDMI ONLY
COLOR_MAP = {
    "0": "---",
    "1": "RGB Limit",
    "2": "RGB Full",
    "3": "YcbCr444",
    "4": "YcbCr422"
    }

# HDMI ONLY
FORMAT_BIT_MAP = {
    "0": "---",
    "1": "24bit (8bit*3)",
    "2": "30bit (10bit*3)",
    "3": "36bit (12bit*3)",
    "4": "48bit (16bit*3)"
    }

COLOR_SPACE_MAP = {
    "0": "---",
    "1": "Standard",
    "2": "xvYCC601",
    "3": "xvYCC709",
    "4": "sYCC",
    "5": "AdobeYCC601",
    "6": "AdobeRGB"
    }

def decode_vst(s: str) -> Optional[str]:
    if not s.startswith('VST'):
        return None
    print(f"Debug is {config.DEBUG}")
    if config.DEBUG:
        report(f"Decoding {s}\n")
    result = ""
    s = "-" + s[3:] # for off-by-one
    signal = SIGNAL_MAP.get(s[1], "Unknown")
    result += f"Signal: {signal}\n"
    sformat = SIGNAL_FORMAT_MAP.get(s[2:4], "Unknown")
    result += f"Input resolution: {sformat}\n"
    aspect = ASPECT_MAP.get(s[4], "Unknown")
    result += f"Aspect: {aspect}\n"
    color = COLOR_MAP.get(s[5], "Unknown")
    result += f"Input color format: {color}\n"
    ibit = FORMAT_BIT_MAP.get(s[6], "Unknown")
    result += f"Input bit (HDMI only): {ibit}\n"
    cspace = COLOR_SPACE_MAP.get(s[7], "Unknown")
    result += f"Input extend color space (HDMI only): {cspace}\n"
    oformat = SIGNAL_FORMAT_MAP.get(s[8:10], "Unknown")
    result += f"Output resolution: {oformat}\n"
    oaspect = ASPECT_MAP.get(s[10], "Unknown")
    result += f"Output aspect: {oaspect}\n"
    ocolor = COLOR_MAP.get(s[11], "Unknown")
    result += f"Output color format (HDMI only): {ocolor}\n"
    obit = FORMAT_BIT_MAP.get(s[12], "Unknown")
    result += f"Output bit (HDMI only): {obit}\n"
    ospace = COLOR_SPACE_MAP.get(s[13], "Unknown")
    result += f"Output extend color space (HDMI only): {ospace}\n"
    mrecommend = SIGNAL_FORMAT_MAP.get(s[14:16], "Unknown")
    result += f"Monitor recommend resolution information: {mrecommend}\n"
    mdcolor = FORMAT_BIT_MAP.get(s[16], "Unknown")
    result += f"Monitor DeepColor: {mdcolor}\n"
    # ... TODO
    return result


def decode_vta(s: str) -> Optional[str]:
    if not s.startswith('VTA'):
        return None
    return None

