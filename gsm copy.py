import sys
import time
from serialcom.comm import COMM

#serial_port = '/dev/ttyACM0'
#serial_port = '/dev/ttyUSB1'
serial_port = "/dev/serial0"

phone = COMM(serial_port)

# Verify connection
state = phone.connection_status()
if not state:
    sys.exit("No Connection")

# Setup session
print(phone.setup())

joana = "+351919365209"
filipe = "+351915884402"
rui = "+351938370555"
luisa = "+351915423077"
camila = "+351919785478"

meter = "+351962156457"
serial = "156318"

# phone.call(camila)

# phone.call(camila)
# phone.get_fund()

#phone.read_sms(8, 'SM')
#phone.read_sms(29, 'ME')
#phone.read_sms(30, 'ME')
#phone.read_sms(37, 'ME')

# stor = phone.get_storages()
# print(stor)


# phone.read_storage_messages("ME")
# phone.delete_storage_message(3, "ME")
# phone.empty_storage_message("SM")

to = rui
msg = "Msg to send here"

# phone.send_sms(to, msg)
# phone.get_fund()
# phone.check_incoming()

#value = phone.get_storage_status("MT")
# print(value['used'])

# Open internet connection
state = phone.open_internet_connection()
if not state:
    phone.close_internet_connection()

state = phone.open_tcp_connection("TCP", "85.234.128.80", "80")
if not state:
    phone.close_internet_connection()

payload = "GET / HTTP/2"
state = phone.send_tcp_request(payload)
if not state:
    phone.close_internet_connection()

reply = phone.get_http_request()

print(reply)

# Close internet connection
phone.close_internet_connection()
