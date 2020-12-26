import sys
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

phone.call(rui)
phone.check_incoming()
print("press 'q' to hangup")
phone.hangup()

# phone.get_fund()
# phone.check_incoming()
#phone.read_sms(28, 'ME')
#phone.read_sms(29, 'ME')
#phone.read_sms(30, 'ME')
#phone.read_sms(37, 'ME')

# value = phone.get_storage_status("ME")
# print(value)
# phone.read_storage_messages("ME")
#phone.delete_storage_message(3, "ME")
# phone.empty_storage_message("SM")

to = ""
msg = "Msg to send"

# phone.send_sms(to, msg)
# phone.get_fund()
# phone.check_incoming()

# internet connection
# phone.connect_internet()
