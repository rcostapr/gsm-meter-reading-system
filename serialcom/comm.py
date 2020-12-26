import os
import time
import sys
import serial
import keyboard
from io import StringIO
from .simcom import SIMCOM


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


class COMM:

    LINE_FEED = '\r'
    RESET = 'RT'
    CTRL_Z = '\x1A'

    def __init__(self, serial_port):
        try:
            self.ser = serial.Serial(
                serial_port, baudrate=115200, timeout=1)
        except Exception as e:
            sys.exit("Error: {}".format(e))

        self._clip = None
        self._msgid = 0
        self.savbuf = None
        self.modem = SIMCOM(self)

    def connection_status(self) -> bool:
        return self.modem.check_connection()

    def setup(self) -> str:
        return self.modem.setup()

    def exec(self, cmdstr, descr=None):
        # clean buffer
        while self.ser.in_waiting:
            self.ser.readline()

        # print(self.ser.in_waiting)
        if descr:
            print(descr + " ...")
        # execute command
        self.ser.write(cmdstr.encode())
        # discard linefeed etc
        self.ser.readline()

        line = 0
        # Wait for Answer
        while True:
            buf = self.ser.readline()
            if buf:

                if line == 0:
                    self.savbuf = buf
                else:
                    self.savbuf += buf
                line += 1

                # print(line)
                result = convert_to_string(buf)

                # print(result)
                if result == "OK" or "ERROR" in result or result == "NO CARRIER" or "CONNECT" in result or result == "BUSY" or result == "NO ANSWER" or result == "NO DIALTONE":
                    if "ERROR" in result:
                        print(cmdstr.replace(self.LINE_FEED, "") +
                              ": " + convert_to_string(self.savbuf))

                    if result == "NO CARRIER":
                        print(result)
                        return line

                    while self.ser.in_waiting:
                        self.ser.readline()

                    return line

    def connect_internet(self):

        # The value 0 represents SMS PDU mode
        # The value 1 represents SMS TEXT mode.
        self.exec('AT+CMGF=1' + self.LINE_FEED)

        # Codification
        # +CSCS: ("GSM","HEX","IRA","PCCP","PCDN","UCS2","8859-1")
        self.exec('AT+CSCS="GSM"' + self.LINE_FEED)

        # APN Attr
        apn = "internet"
        apn_name = ""
        apn_pass = ""
        apn_mcc = "268"
        apn_mnc = "03"
        apn_type = "IP"
        apn_auth = "PAP"
        apn_dial = "*99#"

        """
        APN
        ---
        Name: internet
        APN: internet
        MCC (Mobile Country Code): 268 (Portugal)
        MNC (Mobile Network Code): 07 (NOS/Optimus)
        APN Type: internet
        AT+CDNSCFG="4.4.4.4","8.8.8.8"
        """

        # REGISTER
        # AT+CREG // GERAN, E-UTRAN – core network used in 2G and 3G mode
        # AT+CGREG // GPRS, GERAN – data services in 2G GSM/GPRS core network
        # AT+CEREG // EPS – (Evolved Packet System) core network used in 4G mode

        """
        Possible values of registration status are,
        0 not registered, MT is not currently searching a new operator to register to
        1 registered, home network
        2 not registered, but MT is currently searching a new operator to register to
        3 registration denied
        4 unknown (e.g. out of GERAN/UTRAN/E-UTRAN coverage)
        5 registered, roaming
        6 registered for "SMS only", home network (applicable only when indicates E-UTRAN)
        7 registered for "SMS only", roaming (applicable only when indicates E-UTRAN)
        8 attached for emergency bearer services only (not applicable)
        9 registered for "CSFB not preferred", home network (applicable only when indicates E-UTRAN)
        10 registered for "CSFB not preferred", roaming (applicable only when indicates E-UTRAN)

        Possible values for access technology are,
        0 GSM
        1 GSM Compact
        2 UTRAN
        3 GSM w/EGPRS
        4 UTRAN w/HSDPA
        5 UTRAN w/HSUPA
        6 UTRAN w/HSDPA and HSUPA
        7 E-UTRAN
        """

        # Check the registration status before before setting up voice or data call
        # AT+CREG=? -> +CREG: (0-2)
        # Configure to return unsolicited result code when network registration is disabled
        # AT+CREG=0
        # Configure to return unsolicited result code  with when network registration is enabled
        # AT+CREG=1
        # Configure to return unsolicited result code when there is change in network registration status or change of network cell
        # AT+CREG=2

        # Enable +CREG: unsolicited result code
        # 2G and 3G mode
        self.exec('AT+CREG=1' + self.LINE_FEED)
        # Check the registration status
        # +CREG: 1,1 -> MT is registered in home PLMN
        # +CREG: 3,1 -> Registration is denied
        # +CREG: 6,1 -> Registered for SMS only
        self.exec('AT+CREG?' + self.LINE_FEED)
        result = self.get_response().split('\r\n')
        if result[0] == "+CREG: 1,1":
            print("GPRS Register on network")
        else:
            print("GPRS NOT Register on network")
            print(result)
            sys.exit()

        # Enable +CGREG: unsolicited result code
        # 2G GSM/GPRS core network
        self.exec('AT+CGREG=1' + self.LINE_FEED)

        # Check the registration status
        # +CGREG: 1,1 -> MT is registered in home PLMN
        # +CGREG: 3,1 -> Registration is denied
        # +CGREG: 6,1 -> Registered for SMS only
        self.exec('AT+CGREG?' + self.LINE_FEED)
        result = self.get_response().split('\r\n')
        if result[0] == "+CGREG: 1,1":
            print("GPRS Enable on network")
        else:
            print("GPRS NOT Enable on network")
            print(result)
            sys.exit()

        # Attach to the network
        # PDP context activate +CGACT
        # The +CGACT command activates or deactivates a Packet Data Network (PDN) connection
        """
        Syntax:

        +CGACT=<state>,<cid>

        The set command parameters and their defined values are the following:

        <state>
            0 – Deactivate
            1 – Activate
        <cid>
            1–11

        The following command example activates a bearer configured with CID 1:

        AT+CGACT=1,1
        OK
        """
        # Detach GPRS
        self.exec('AT+CGATT=0' + self.LINE_FEED)
        # Attach GPRS
        self.exec('AT+CGATT=1,1' + self.LINE_FEED)
        # Attach Profile
        self.exec('AT+CGACT=1,1' + self.LINE_FEED)

        # Check if Data Connection Available
        # Check the GPRS attach status.
        # Must Return +CGATT: 1
        self.exec('AT+CGATT?' + self.LINE_FEED)
        result = self.get_response().split('\r\n')
        result = result[0].split("+CGATT: ")
        if int(result[1]) > 0:
            print("Device is attached to the network : " + result[1])
        else:
            print("Device is NOT attached to the network")
            return

        # Wait for Attach
        time.sleep(1)

        # Define PDP Context (Packet Data Protocol)
        # PDP addresses can be X.25, IP, or both
        # AT+CGDCONT?
        # +CGDCONT: 1,"IP","internet","",0,0
        # +CGDCONT: 2,"IP","umts","",0,0
        """
        CID-> 1
        PDP Type->IP
        APN->umts
        PDP Address->0.0.0.0
        Data Compression->0
        Header Compression->0
        """
        cmdstr = 'AT+CGDCONT=1,"{}","{}","0.0.0.0",0,0'.format(apn_type, apn)
        self.exec(cmdstr + self.LINE_FEED, cmdstr)
        result = self.get_response().split('\r\n')
        print(result[0])

        # Dial UP
        cmdstr = "ATD" + apn_dial
        # Getting Connection
        self.exec(cmdstr + self.LINE_FEED, cmdstr)
        result = self.get_response().split('\r\n')
        print(result[0])

        # Wait for Dial UP and Wait for IP address
        time.sleep(1)

        # Config GPRS and TCP/IP modes

        # Enable to get details of IP address
        # and Port Number of the sender
        # Show Remote IP Address and Port
        # self.exec('AT+CIPSRIP=1' + self.LINE_FEED, "AT+CIPSRIP=1")
        # result = self.get_response().split('\r\n')
        # print(result[0])

        # Set APN Definitions
        # Insert APN, user name and password
        # +CME ERROR: 765 -> "invalid input value"
        #cmdstr = 'AT+CSTT="{}","{}","{}"'.format(apn, apn_name, apn_pass)
        #cmdstr = 'AT+CSTT="{}"'.format(apn_name)
        #self.exec(cmdstr + self.LINE_FEED, cmdstr)
        #result = self.get_response().split('\r\n')
        # print(result[0])

        # Wait for apply definitions
        # time.sleep(1)

        # Make Connection - Bring up the wireless connection
        #self.exec('AT+CIICR' + self.LINE_FEED, 'AT+CIICR')
        #result = self.get_response().split('\r\n')
        # print(result)

        # Wait for bringup
        # time.sleep(6)

        # Gets the dynamic IP address of local
        # module as allotted by GPRS network
        # self.exec('AT+CIFSR' + self.LINE_FEED, 'AT+CIFSR')
        # result = self.get_response().split('\r\n')
        # print(result)
        # sys.exit()

        # Check IP status
        # must return "STATE: IP STATUS" for connection
        #self.exec('AT+CIPSTATUS' + self.LINE_FEED, 'AT+CIPSTATUS')
        #result = self.get_response().split('\r\n')
        # print(result)

        # Get the local IP address
        #self.exec('AT+CIFSR' + self.LINE_FEED, 'AT+CIFSR')
        #result = self.get_response().split('\r\n')
        # print(result)

        # Start a TCP connection to remote address. Port 80 is TCP.
        #cmdstr = 'AT+CIPSTART="TCP","85.234.128.80","80"'
        #self.exec(cmdstr + self.LINE_FEED, cmdstr)
        #result = self.get_response().split('\r\n')
        # print(result[0])

        # Hangup
        time.sleep(2)
        cmdstr = '+++'
        self.exec(cmdstr, "Turn off GPRS")
        time.sleep(2)
        cmdstr = 'AT+CHUP'
        self.exec(cmdstr + self.LINE_FEED, cmdstr)
        result = self.get_response().split('\r\n')
        print(result[0])

    def send_sms(self, destno, msgtext):

        # Hangup
        cmdstr = 'ATH' + self.LINE_FEED
        self.exec(cmdstr)

        print("Sending SMS ...")
        # The value 0 represents SMS PDU mode and the value 1 represents SMS TEXT mode.
        self.exec('AT+CMGF=1' + self.LINE_FEED)

        # Codification
        # +CSCS: ("GSM","HEX","IRA","PCCP","PCDN","UCS2","8859-1")
        # Set Character set to HEX - 1
        # AT+CSCS="HEX"
        # Set Character set to UCS2 - 16-bit universal multiple-octet coded character set
        # AT+CSCS="UCS2"
        # Set Character set to 8859-1 = ISO 8859 Latin 1 character set
        # AT+CSCS="8859-1"
        self.exec('AT+CSCS="IRA"' + self.LINE_FEED)

        # Message Text Memory index
        #  AT+CPMS="SM" Sim Card
        #  AT+CPMS="ME" GSM/GPRS modem or mobile phone
        storage = "SM"
        self.exec('AT+CPMS="{}"'.format(storage) + self.LINE_FEED)

        # number
        number = destno

        # payload
        payload = msgtext.encode()

        # clean buffer
        while self.ser.in_waiting:
            self.ser.readline()

        # Open Connection
        cmdstr = 'AT+CMGS="{}"'.format(number) + self.LINE_FEED
        print("Send to " + destno + " ...")
        # execute command
        self.ser.write(cmdstr.encode())

        # discard linefeed etc
        self.ser.readline()

        line = 0
        # Wait for Answer
        while True:
            buf = self.ser.readline()
            if buf:

                if line == 0:
                    self.savbuf = buf
                else:
                    self.savbuf += buf
                line += 1

                # print(line)
                result = convert_to_string(buf)

                print(result)
                if result == "OK" or "ERROR" in result or result == "NO CARRIER":
                    if "ERROR" in result:
                        print(cmdstr.replace(self.LINE_FEED, "") +
                              ": " + convert_to_string(self.savbuf))

                    if result == "NO CARRIER":
                        break

                    while self.ser.in_waiting:
                        self.ser.readline()
                    return line

                if result == ">":
                    # read to insert message
                    break

        # Write Message
        print(msgtext)
        self.ser.write(payload)

        # send
        cmdstr = self.CTRL_Z
        self.ser.write(cmdstr.encode())

        line = 0
        # Wait for Answer
        while True:
            buf = self.ser.readline()
            if buf:

                if line == 0:
                    self.savbuf = buf
                else:
                    self.savbuf += buf
                line += 1

                # print(line)
                result = convert_to_string(buf)

                # print(result)
                if result == "OK" or "ERROR" in result:
                    if "ERROR" in result:
                        print(cmdstr.replace(self.LINE_FEED, "") +
                              ": " + convert_to_string(self.savbuf))

                    while self.ser.in_waiting:
                        self.ser.readline()

                    # Hangup
                    cmdstr = 'ATH' + self.LINE_FEED
                    self.exec(cmdstr)
                    return line

    def read_sms(self, id, storage: str = None):
        # The value 0 represents SMS PDU mode and the value 1 represents SMS TEXT mode.
        self.exec('AT+CMGF=0' + self.LINE_FEED)
        # +CMS ERROR: 321 "Invalid Memory Index"
        # +CMS ERROR: 518 "storage type is invalid" -> AT+CMGF=1
        # AT+CPMS="ME","SM","MT"
        """
        SM. It refers to the message storage area on the SIM card.

        ME. It refers to the message storage area on the GSM/GPRS modem or mobile phone. Usually its storage space is larger than that of the message storage area on the SIM card.

        MT. It refers to all message storage areas associated with the GSM/GPRS modem or mobile phone. For example, suppose a mobile phone can access two message storage areas: "SM" and "ME". The "MT" message storage area refers to the "SM" message storage area and the "ME" message storage area combined together.

        BM. It refers to the broadcast message storage area. It is used to store cell broadcast messages.

        SR. It refers to the status report message storage area. It is used to store status reports.

        TA. It refers to the terminal adaptor message storage area.
        """
        # Message Text Memory index
        #  AT+CPMS="SM" Sim Card
        #  AT+CPMS="ME" GSM/GPRS modem or mobile phone
        if storage:
            self.exec('AT+CPMS="{}"'.format(storage) + self.LINE_FEED)

        # Read Message ID
        cmdstr = 'AT+CMGR={}' + self.LINE_FEED
        lines = self.exec(cmdstr.format(id), "Reading SMS ID: {}".format(id))

        if lines <= 2:
            print("Not Found")

        message = self.get_response().split('\r\n')
        # message = self.savbuf
        # print(message)
        # return lines
        if lines > 2:
            header = message[0].split(',')
            if len(header) == 3:
                at = header[0].split(': ')[1]
                # print(at)
                statusDict = {
                    "0": "REC READ",
                    "1": "REC UNREAD",
                    "2": "STO SENT",
                    "3": "STO UNSENT",
                    "4": "ALL"
                }
                status = statusDict[at]
                # received_from = UCS2.decode(header[1].replace('"', ''))
                # received_name = UCS2.decode(header[2].replace('"', ''))

                # TODO:Decode
                received_from = header[1].replace('"', '')
                received_value = header[2].replace('"', '')

                # received_date = header[3].replace('"', '')
                # received_time = header[4].replace('"', '')

                print("Status: " + status)
                print("From: " + bytearray.fromhex(received_from).decode())

        if lines > 3:
            """
            msg = SMSDeliver.decode(StringIO(message[1]))
            # print(msg)
            smsc_number = msg["smsc"]["number"]
            sended_at = msg["scts"]
            date_time = sended_at.strftime("%Y/%m/%d, %H:%M:%S")
            sended_number = msg["sender"]["number"]

            # print("SMSC: +" + smsc_number)
            print("Number: +" + sended_number)
            print("Date Time: +" + date_time)
            print("Message:")
            print(msg["user_data"]["data"])
            print("")
            """

        return lines

    def get_fund(self):

        # Hangup
        cmdstr = 'ATH' + self.LINE_FEED
        self.exec(cmdstr)

        # The value 0 represents SMS PDU mode and the value 1 represents SMS TEXT mode.
        self.exec('AT+CMGF=1' + self.LINE_FEED)

        # Codification
        self.exec('AT+CSCS="GSM"' + self.LINE_FEED)

        cmdstr = 'ATD*#123#' + self.LINE_FEED
        # Getting Funds
        lines = self.exec(cmdstr)
        result = self.get_response().split('\r\n')
        message = result[0].split(",")
        if len(message) > 1:
            message = message[1].split("\n")[0].replace('"', '')
            if message:
                print(message)
            else:
                print(result)

        # Hangup
        cmdstr = 'ATH' + self.LINE_FEED
        self.exec(cmdstr)

    def delete_sms(self, id, storage):
        if storage:
            # Set Memory Storage
            # +CPMS: ("SM","ME","SR"),("SM","ME","SR"),("SM","ME")
            cmdstr = 'AT+CPMS="{}"'.format(storage) + self.LINE_FEED
            self.exec(cmdstr)

        cmdstr = 'AT+CMGD={}'.format(id) + self.LINE_FEED
        self.exec(cmdstr, "Delete SMS ID: {}".format(id))
        result = self.get_response().split('\r\n')
        print(result)

    def check_incoming(self):
        while True:
            buf = self.ser.readline()
            if buf:
                buf = convert_to_string(buf)
                print(buf)
                params = buf.split(',')

                # Handle new incoming message
                if params[0][0:5] == "+CMTI":
                    print("Receiving Text Message ...")

                    # Message ID
                    self._msgid = int(params[1])

                    # Memory index
                    memory_index = params[0][7:]

                    # Set Memory Storage
                    cmdstr = 'AT+CPMS=' + memory_index + self.LINE_FEED
                    self.exec(cmdstr)

                    # Read Message
                    self.read_sms(self._msgid)

                # Handle no carrier
                elif params[0] == "NO CARRIER":
                    # @todo handle
                    pass

                # Handle new incoming Message
                elif params[0] == "RING" or params[0][0:5] == "+CLIP":
                    # @todo handle
                    pass

            if keyboard.is_pressed('q'):
                break

    def read_storage_messages(self, storage="ME"):
        # Set Memory Storage
        # +CPMS: ("SM","ME","SR"),("SM","ME","SR"),("SM","ME")
        cmdstr = 'AT+CPMS="' + storage + '"' + self.LINE_FEED
        self.exec(cmdstr)
        result = self.get_response().split('\r\n')
        status = result[0].split(" ")
        if status[0] == "+CPMS:":
            values = status[1].split(",")
            if len(values) > 2:
                used = values[0]
                max_storage = values[1]
                print("Storage {} :: Used:{} Max:{}".format(
                    storage, used, max_storage))

                # Read Messages
                i = int(used)
                while i > 1:
                    self.read_sms(i)
                    i -= 1

    def get_storage_status(self, storage="ME"):
        # Set Memory Storage
        # +CPMS: ("SM","ME","SR"),("SM","ME","SR"),("SM","ME")
        cmdstr = 'AT+CPMS="' + storage + '"' + self.LINE_FEED
        self.exec(cmdstr)
        result = self.get_response().split('\r\n')
        status = result[0].split(" ")
        if status[0] == "+CPMS:":
            values = status[1].split(",")
            if len(values) > 2:
                used = values[0]
                max_storage = values[1]
                return {
                    "used": used,
                    "max": max_storage
                }

    def delete_storage_message(self, id, storage="ME"):
        # Set Memory Storage
        # +CPMS: ("SM","ME","SR"),("SM","ME","SR"),("SM","ME")
        cmdstr = 'AT+CPMS="' + storage + '"' + self.LINE_FEED
        self.exec(cmdstr)

        # Delete Message
        cmdstr = 'AT+CMGD={}'.format(id) + self.LINE_FEED
        self.exec(cmdstr, "Delete Message ID: {}".format(id))
        result = self.get_response().split('\r\n')
        print(result[0])

    def empty_storage_message(self, storage="ME"):
        # Set Memory Storage
        # +CPMS: ("SM","ME","SR"),("SM","ME","SR"),("SM","ME")
        cmdstr = 'AT+CPMS="' + storage + '"' + self.LINE_FEED
        self.exec(cmdstr)

        value = self.get_storage_status(storage)
        total = value["used"]

        id = int(total)
        while id > 1:
            # Delete Message
            cmdstr = 'AT+CMGD={}'.format(id) + self.LINE_FEED
            self.exec(cmdstr, "Delete Message ID: {}".format(id))
            result = self.get_response().split('\r\n')
            print(result[0])
            id -= 1

    def call(self, number: str):
        """
        Make a Phone Call
        -----------------
        number to call
        """
        cmdstr = 'ATD{};'.format(number)
        self.exec(cmdstr + self.LINE_FEED)

    def hangup(self):
        """
        Hanguyp a Phone Call
        -----------------
        """
        cmdstr = 'ATH'
        self.exec(cmdstr + self.LINE_FEED)
        message = self.get_response().split('\r\n')
        value = message[0]
        if value != 'OK':
            return False
        return True

    def get_msgid(self):
        return self._msgid

    def get_response(self):
        return convert_to_string(self.savbuf)
