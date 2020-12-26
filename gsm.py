from serialcom.comm import COMM
from smspdu.codecs import UCS2

serial_port = '/dev/ttyACM0'
#serial_port = '/dev/ttyUSB1'

phone = COMM(serial_port)

# Verify connection
phone.connection_status()

# Setup session
phone.setup()

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

joana = "+351919365209"
filipe = "+351915884402"
rui = "+351919873697"
luisa = "+351915423077"

meter = "+351962156457"
serial = "156318"

to = ""
msg = "Msg to send"

# phone.send_sms(to, msg)
# phone.get_fund()
# phone.check_incoming()

# internet connection
phone.connect_internet()
