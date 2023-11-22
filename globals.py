from urllib import request

serial_out_buffer = []
state = None
smartHome = None
fireBase = None
global_heating: bool = False
global_cooling: bool = True
config = None

def is_internet_available():
    try:
        request.urlopen('https://www.google.com', timeout=1)
        return True
    except request.URLError as err:
        return False
