from modules.crafting import *
from scapy.all import RadioTap, Dot11, Dot11ProbeReq, Dot11Elt, sendp
from random import randint

class Send:
    """
    Class for sending messages
    """
    def __init__(self, password, interface, ssid, channel, username, window, clear=True):
        self.interface = interface
        self.password = password
        self.ssid = ssid
        self.username = username
        self.channel = channel
        self.ammarage = getammarage(password)
        self.mac = random_mac(password, username)
        self._window = window
        self._clear = clear

        
    def probe_req(self, supported_rates : bytes, sc : int):
        """
        Crafting the probe request the more realistic way :)
        """
        extended_rates = b'\x0c\x12\x18\x24\x30\x48\x60\x6c'
        packet = RadioTap() / \
            Dot11(type=0, subtype=4, addr1="ff:ff:ff:ff:ff:ff", addr2=self.mac, addr3=self.mac, SC=sc << 4) / \
            Dot11ProbeReq() / \
            Dot11Elt(ID=0, info=self.ssid) / \
            Dot11Elt(ID=1, info=supported_rates) / \
            Dot11Elt(ID=50, info=extended_rates) /  \
            Dot11Elt(ID=3, info=bytes([self.channel])) / \
            Dot11Elt(ID=7, info=b'FR\x04\x01\x0b\x14\x01\x0c\x0c') / \
            Dot11Elt(ID=33, info=b'\x00\x14') / \
            Dot11Elt(ID=45, info=b'\x26\x22\x23\x23\x21\xf3\x21\x00\x00\x00\x00\x00\x01'*2) / \
            Dot11Elt(ID=221, info=b'\xf0\x81\x75\x04\x10\x4a\x00\x01\x10') 

        sendp(packet, iface=self.interface, verbose=0)

    def send(self, message):
        """
        Split the message in words and send them one by one 
        """
        for word in message.split(" "):
            rates = encode(self.ammarage[0] + word, self.password)
            random.seed(None)
            sc = randint(10, 1000)
            self.probe_req(rates, sc)
            self._window.clear() if self._clear == True else 1+1