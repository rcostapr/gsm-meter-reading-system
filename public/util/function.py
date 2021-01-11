import ipaddress


def convert_to_string(buf):
    try:
        tt = buf.decode('utf-8').strip()
        return tt
    except UnicodeError:
        tmp = bytearray(buf)
        for i in range(len(tmp)):
            if tmp[i] > 127:
                tmp[i] = ord('#')
        return bytes(tmp).decode('utf-8').strip()


def is_valid_ipaddress(str_ip: str) -> bool:
    """Validate if a given string is an IP address

    Args:
        str_ip (str): IP Address to validate

    Returns:
        bool: True if is a valid IP address False otherwise
    """
    try:
        ipaddress.ip_address(str_ip)
        return True
    except ValueError:
        return False
