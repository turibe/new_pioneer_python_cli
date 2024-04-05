
import json
import os


# Default set. To read query the AVR's actual names and save to json, use "learn":

defaultInputSourcesMap = {
    "00" : "PHONO",
    "01" : "CD",    
    "02" : "TUNER",
    "04" : "DVD",
    "05" : "TV",
    "06" : "SAT/CBL",
    "10" : "VIDEO",
    "12" : "MULTI CH IN",
    "13" : "USB-DAC",
    "15" : "DVR/BDR",
    "17" : "iPod/USB",
    "19" : "HDMI1",
    "20" : "HDMI2",
    "21" : "HDMI3",
    "22" : "HDMI4",
    "23" : "HDMI5",
    "24" : "HDMI6",
    "25" : "BD",
    "26" : "NETWORK", # cyclic
    "31" : "HDMI", # cyclic
    "33" : "ADAPTER PORT",
    "34" : "HDMI7",
    "38" : "INTERNET RADIO",
    "40" : "SiriusXM",
    "41" : "PANDORA",
    "44" : "MEDIA SERVER",
    "45" : "Favorites",
    "47" : "DMR",
    "48" : "MHL" # device input, not working on test AVR
}

def check_exists(s):
    if os.path.isfile(s):
       return s
    return None

sources_map_filename = "pioneer_avr_sources.json"

class SourceMap:
    
    def __init__(self):
        self.source_map = {}
        self.inverse_map = {}
        self.alias_map = {}
        self.init_from_map(defaultInputSourcesMap)

    def init_from_map(self, initmap):
        for (k,v) in initmap.items():
            self.source_map[k] = v
            self.register_reverse_source(k, v)
        # the value here is the command for changing to the source given by the key
        self.add_aliases()

    def get(self, *args, **kwargs):
        return self.source_map.get(*args, **kwargs)

    def read_from_file(self):        
        cwd = os.getcwd()
        map_file = check_exists(f"{cwd}/{sources_map_filename}") or check_exists(os.path.expanduser(f"~/{sources_map_filename}"))
        if map_file:
            read_map = {}
            print(f"Reading sources map from {map_file}")
            with open(map_file, "r") as f:
                try:
                    read_map= json.load(f)
                except Exception as e:
                    print(f"Error reading map from {map_file}", e)
            self.init_from_map(read_map)
        else:
            print(f'Use "learn" to update sources, "save" to save them')

    def save_to_file(self):
        with open(sources_map_filename, "w") as outfile:
                json.dump(self.source_map, outfile)
        print(f"Wrote sources map to {sources_map_filename}")

    def register_reverse_source(self, k, v):
        newk = v.lower()    
        self.inverse_map[newk] = k + "FN"

    def update_source(self, name: str, id: str):
        print(f"Updating source {name} ({id})")
        self.source_map[id] = name
        self.register_reverse_source(id, name)
        alias = self.alias_map.get(name)
        if alias:
            self.check_aliases(name, alias)

    def add_alias(self, a: str, b: str):
        a = a.lower()
        b = b.lower()
        self.alias_map[a] = b
        self.alias_map[b] = a
        self.check_aliases(a,b)

    def check_aliases(self,a,b):
        if self.inverse_map.get(a) is None and self.inverse_map.get(b):
            self.inverse_map[a] = self.inverse_map[b]
            # print(f"{a} -> {b}")
        else:
            if self.inverse_map.get(b) is None and self.inverse_map.get(a):
                inverseSourcesMap[b] = inverseSourcesMap[a]
                # print(f"{b} -> {a}")

    def add_aliases(self):
        self.add_alias("apple", "appletv")
        self.add_alias("amazon", "amazontv")
        self.add_alias("radio", "tuner")
        self.add_alias("iradio", "internet radio")

    def learn_input_from(self, s):
        id = s[0:2]
        name = s[3:]
        if self.source_map.get(id, None) != name:
            print(f"Updating source name {name} for {id}")
            self.update_source(name, id)

