from scapy.all import *
import pyshark, curses, base64
from modules.crafting import *
from modules.send import Send
from modules.filecrafting import *
class Receive:
    """
    Class for receiving messages 
    """
    def __init__(self, password, interface, username, window, send_window):
        self.interface = interface
        self.password = password
        self.username = username
        self.window = window
        self.messages = []
        self._ammarage = getammarage(password)
        self._mac = random_mac(password, username)
        self._send_window = send_window
        
    
    def listen(self):
        """
        Listen for messages in live, decode and send feedback
        """
        with pyshark.LiveCapture(interface=self.interface) as cap:
            for packet in cap.sniff_continuously():
                if len(packet.layers) > 3:
                    layer2, layer3 = packet.layers[2], packet.layers[3]
                    for field in layer3._all_fields:
                        if field == "wlan.supported_rates" and layer2.sa != self._mac:
                            alldata = [str(rate.show).replace("0x", "") for rate in layer3.wlan_supported_rates.all_fields]
                            # Check if ammarage
                            if "".join(alldata)[:8] == self._ammarage[1]:
                                dcms = decode(alldata, self.password)
                                s2 = Send(self.password, self.interface, "", 1, self.username, self._send_window, False)
                                
                                # Check if normal messages
                                if dcms == "EOC" and self.messages[0] == "msg":
                                    username = self.messages[-1]
                                    if username == "System": # System Messages only
                                        self.window.addstr(f"System << {' '.join(self.messages[1:-1])}\n", curses.A_DIM | curses.A_ITALIC)
                                    else: # Normal messages Feedback Sending
                                        message = ''.join(self.messages[1:-1])
                                        message = message.replace("0_0", " ")
                                        self.window.addstr(f"{username} << {message}\n", curses.A_ITALIC | curses.A_BOLD)
                                        s2.send(f"msg Message Delivered to {self.username} System EOC")
                                    self.messages = [] 
                                    
                                # Check if file 
                                elif dcms == "EOP" and self.messages[0] != "msg": 
                                        username = self.messages[-1]
                                        datas = "".join(self.messages[1:-1])
                                        self.window.addstr(f"{username} << Received File {self.messages[0]} {len(datas)}\n", curses.A_ITALIC | curses.A_BOLD)
                                        self.window.refresh()
                                        decoded = file_decoder(datas)
                                        
                                        if decoded == b"":
                                            self.window.addstr(f"Decompression Failed")
                                            s2.send(f"msg Error Delivering file to {self.username} System EOC")
                                            
                                        else:
                                            with open(f"files/{self.messages[0]}", "wb") as f:
                                                f.write(decoded) 
                                            s2.send(f"msg File Delivered to {self.username} System EOC")
                                        self.messages = []
                                else:
                                    self.messages.append(dcms)
                                self.window.refresh()
                                # self.messages = []
                         