"""Proxii v2.0"""

import  threading, curses, os, re, string, random
from datetime import datetime
from modules.crafting import *
from modules.filecrafting import *
from modules.receive import Receive
from modules.congested import *
from modules.send import Send
import argparse as ap
from tkinter.filedialog import askopenfilename

parser = ap.ArgumentParser(description="Proxii")
parser.add_argument("-i", "--interface", help="Interface to use", required=True)
parser.add_argument("-u", "--username", help="Username to use", required=True)
parser.add_argument("-p", "--secret-key", help="Password to use", required=True)
parser.add_argument("-s", "--ssid", help="SSID to use")

# Parse the arguments
args = parser.parse_args()
interface = args.interface
ssid = args.ssid if args.ssid else ""
username = args.username
secret_key = args.secret_key

date = datetime.now().strftime("%H:%M:%S")

def check_size(term) -> None:
    if os.get_terminal_size()[0] < 60 or os.get_terminal_size()[1] < 25:
        term.clear()
        term.addstr(0, 0, f"Terminal too small. Press Enter to continue", curses.A_BOLD)     
        term.getch()
        exit()

def main(term) -> None:
    user_input = ""
    channel = 1
    # Prepare the screen
    check_size(term)
    term.clear()
    height, width = term.getmaxyx()
    receive_window = term.subwin(height // 2, width, 0, 0)
    send_window = term.subwin(2, width, height - 2, 0)
    
    def _interface(receive_window, send_window):
        """
        interface Display
        """
        lines = [f"          Welcome to Proxii v2.0",
                f"          /{'─'*30}\\",
                f"        Username   : {username}",
                f"        Secret Key : {secret_key}",
                f"        Interface    : {interface}",
                f"          \\{'─'*30}/",
                ""]
        
        for i, line in enumerate(lines):
            receive_window.addstr(i, (width - len(line)-10) // 2, line, curses.A_BOLD)
        receive_window.addstr(10, 0, f"Incomming Messages : \n{'─'*20} \n\n", curses.A_BOLD)
        receive_window.refresh()
        send_window.scrollok(True)
        receive_window.scrollok(True)
        send_window.addstr(0, 0,f"{"─" * (receive_window.getmaxyx()[1]-29)}[ Channel : {channel} ({usage(channel, interface) })% ]────\n{date} >> ", curses.A_BOLD)

    # Start the chat
    r = Receive(secret_key, interface, username, receive_window, send_window)
    threading.Thread(target=r.listen).start()
    
    s = Send(secret_key, interface, ssid, random.randint(1, 100), username, send_window)
    s.send(f"msg New User '{username}' has joined the chat! System ␃")
    _interface(receive_window, send_window)
    
    # Shitty Loop but it works
    while True:
        if curses.is_term_resized(height, width):
            check_size(term)
            height, width = term.getmaxyx()
            receive_window = term.subwin(height // 2, width, 0, 0)
            send_window = term.subwin(2, width, height - 2, 0)
            term.clear()
            term.refresh()
            _interface(receive_window, send_window)
            send_window.addstr(0, 0,f"{"─" * (receive_window.getmaxyx()[1]-29)}[ Channel : {channel} ({usage(channel, interface)})% ]────\n{date} >> ", curses.A_BOLD)
            send_window.refresh()
            
        key = send_window.getch()
        if key == ord('\n'):
            if user_input.strip():
                normalstrings = [x for x in user_input if x in string.printable]
                user_input = "".join(normalstrings)
                # Checking for basic commands
                try:
                    isfile = re.findall(r"^(.+)\/([^/\s]+\.[a-zA-Z0-9]+)(?=\s*$)", user_input)[0]
                except:
                    isfile = False
                    
                if user_input[:2] == "!c": 
                    if user_input[3:7].isdigit():
                        channel = int(user_input[2:])
                        os.system(f"sudo iw {interface} set channel {channel}")
                        s.send(f"msg {username} jumped on channel : {channel} System ␃")
                    else:
                        receive_window.addstr("Invalid channel number.\n", curses.A_BOLD)

                elif user_input[:5] == "!info":
                    receive_window.addstr(f"Informations : \n\n  Channel : {channel} ({usage(channel, interface)})% \n  Interface : {interface}\n  Secret Key : {secret_key}\n  Username : {username}\n  MAC : {random_mac(secret_key, username)}\n\n", curses.A_BOLD)
                    
                # Checking for files
                elif isfile:
                    file = f"{isfile[0]}/{isfile[1]}"
                    usutmp = spacer(file_encoder(file.replace("'", ""))) # File encoder
                    text = f"{file.split("/")[-1].replace(" ", "_")} {usutmp} {username} ␄" 
                    send_window.addstr(0, 0,f"{"─" * (receive_window.getmaxyx()[1]-29)}[ Channel : {channel} ({usage(channel, interface)})% ]────\n{date} >> Sending file (Estimated time: {int((len(usutmp)*0.000231))} seconds)...", curses.A_BOLD)
                    send_window.refresh()
                    s.send(text)
                    
                else:
                    user_input_a = user_input.replace(" ", "0_0") 
                    number = random.randint(5, 50) #haha idk i think 5,50 is a good range
                    user_input_b = " ".join([user_input_a[i:i+number] for i in range(0, len(user_input_a), number)]) # Just to make word lenght unpredictable
                    text = f"msg {user_input_b} {username} ␃"
                    s.send(text) 
                    receive_window.addstr(f"{username} >> {user_input}\n")
                    
                    
                user_input = ""
                send_window.move(0, 0)
                send_window.clrtoeol()
                send_window.addstr(0, 0, f"{"─" * (receive_window.getmaxyx()[1]-29)}[ Channel : {channel} ({usage(channel, interface)})% ]────\n{date} >> ", curses.A_BOLD)
                receive_window.refresh()
                send_window.refresh()

        elif key == 127: 
            if len(user_input) > 0:
                user_input = user_input[:-1]
                y, x = send_window.getyx()
                if x > 0:
                    send_window.move(y, x - 1)
                else:
                    _, maxx = send_window.getmaxyx()
                    send_window.move(y - 1, maxx - 1)
                send_window.delch()
        else:
            user_input += chr(key)
            send_window.addch(key)


try:
    curses.wrapper(main)

except Exception as e:
    print(f"An error occured : {e}")
    os.system(f"ifconfig {interface} down && iwconfig {interface} mode managed && ifconfig {interface} up && systemctl restart NetworkManager")
    os._exit(1) # because exit is shit to kill blocked process

except KeyboardInterrupt:
    print("Exiting...")
    os.system(f"ifconfig {interface} down && iwconfig {interface} mode managed && ifconfig {interface} up && systemctl restart NetworkManager")
    exit(0)
