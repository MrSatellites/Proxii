import subprocess, re, os
from scapy.all import *

def list_channels():
    channels = subprocess.check_output(["iw", "list"]).decode().split("\n")
    channels = [channel for channel in channels if "MHz " in channel]
    channelt = {}
    for channel in channels:
        if "IR" not in channel and "disabled" not in channel and "in" not in channel:
            channel = re.findall(r"[0-9]+", channel.split("(")[0])[2:]
            if channel != []:
                channelt[(int(channel[0]))] = 0
    return channelt

def usage(channel, interface):
    os.system(f"iwconfig {interface} channel {channel}")
    usage = int(f"{len(list(sniff(timeout=0.7, count=100, iface=interface)))}")
    return usage
