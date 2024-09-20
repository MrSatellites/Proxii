import brotli, base64

def file_encoder(file : str) -> str:
    """
    Takes a file and returns it encoded and compressed
    """
    with open(file, "rb") as f:
        data = f.read()
    data = brotli.compress(data)
    encoded = base64.b85encode(data)
    return encoded.decode('utf-8')

def file_decoder(data : str ) -> str:
    """
    Take datas and return them decompressed to write to a file
    """
    data = data.replace(" ", "") 
    decoded = base64.b85decode(data)
    try:
        decoded = brotli.decompress(decoded)
        return decoded
    except:
        print("Decompression Failed")
        return b""

def spacer(data : str ) -> str:
    """
    Add space all the 240 characters to keep packet under 255
    """
    return " ".join(data[i:i+240] for i in range(0, len(data), 240))
