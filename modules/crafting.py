import random, string, hashlib, os
letters = string.printable + "␄␃"

def secret(pswd):
    """
    Create a dictionary with unique random bytes for each letter in the alphabet based on the password given.
    """
    random.seed(pswd)
    bytes_list = list(range(1, 256))
    random.shuffle(bytes_list) 
    dicta = {}
    for i, letter in enumerate(letters):
        dicta[letter] = bytes([bytes_list[i]])
    return dicta

def encode(txt, password):
    """
    Encode a string with the dictionary created by the secret function.
    """
    dicta = secret(password)
    encoded_bytes = b""
    for char in txt:
        try:
            encoded_bytes += dicta[char]
        except KeyError:
            continue
    return encoded_bytes

def decode(hexlist, password):
    """
    Decode a list of hex values with the dictionary created by the secret function.
    """
    dicta = secret(password)
    for key in dicta:
        dicta[key] = dicta[key].hex()
    
    # Invert the dic ;)
    inverted_dict = {v: k for k, v in dicta.items()}
    decoded_str = ""
    for hex_value in hexlist:
        try:
            decoded_str += inverted_dict[hex_value]
        except KeyError:
            continue
    return decoded_str[8:]

def getammarage(pswd):
    """
    Generate the amarage value based on the password.
    """
    amar = pswd[::-1]
    amar = hashlib.md5(amar.encode()).hexdigest()
    amar = amar[:8].replace("a", "0")[::-1]
    return amar, encode(amar, pswd).hex()[:8]


def random_mac(password, username):
    hostname = os.popen("hostname").read().strip()
    random.seed(password + username + hostname)
    return ":".join(["%02x" % random.randint(0, 255) for _ in range(6)])
