import os, subprocess, time
cwd = os.getcwd()

print("Checking for required packages...")
# Check Python3
if subprocess.call(["which", "python3"]) != 0:
    if "arch" in subprocess.check_output(["lsb_release", "-a"]).decode().lower():
        subprocess.call(["sudo", "pacman", "-S", "python3", "python-pip"])
    elif "ubuntu" in subprocess.check_output(["lsb_release", "-a"]).decode().lower():
        subprocess.call(["sudo", "apt-get", "install", "-y", "python3", "python3-pip"])
 
if subprocess.call(["which", "tshark"]) != 0:
    if "arch" in subprocess.check_output(["lsb_release", "-a"]).decode().lower():
        subprocess.call(["sudo", "pacman", "-S", "wireshark-cli"])
    elif "ubuntu" in subprocess.check_output(["lsb_release", "-a"]).decode().lower():
        subprocess.call(["sudo", "apt-get", "install", "-y", "tshark"])
        
# Check python3 modules
print("Checking for required modules...")
try:
    import pyshark, scapy, curses, brotli
except ImportError:
    print(f"Missing Depencies, installing them for you ...")
    os.system("pip3 install -r requirements.txt")

# Putting interface in monitor mode
interfaces = subprocess.check_output(["ip", "link", "show"]).decode().splitlines()
for line in interfaces:
    if "wl" in line:
        interface = line.split(":")[1].strip()
        break
else:
    print("No wlan interface found")
    exit(1)

os.system(f"sudo systemctl stop NetworkManager && ifconfig {interface} down && iwconfig {interface} mode monitor && ifconfig {interface} up")
interface = interface + "mon" if subprocess.call(["ip", "link", "show", interface + "mon"]) == 0 else interface
os.system("clear")
os.system(f"python3 {cwd}/main.py -i {interface}")

