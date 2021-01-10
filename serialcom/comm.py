import os
import time
import sys
import serial
import datetime
import ipaddress
from io import StringIO
from .simcom import SIMCOM
from util.function import convert_to_string
from util.function import is_valid_ipaddress


class COMM:

    LINE_FEED = '\r'
    RESET = 'RT'
    CTRL_Z = '\x1A'
    ESC = '\x1B'

    def __init__(self, serial_port):
        try:
            self.ser = serial.Serial(
                serial_port, baudrate=115200, timeout=1)
        except Exception as e:
            sys.exit("Error: {}".format(e))

        self._clip = None
        self._msgid = 0
        self.savbuf = None
        self.http_request = ""
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

        self.wait_answer(cmdstr)

    def wait_answer(self, cmdstr=None):
        """
        Wait for Answer
        """
        line = 0
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
                if "OK" in result or "ERROR" in result or result == "NO CARRIER" or "CONNECT" in result or result == "BUSY" or result == "NO ANSWER" or result == "NO DIALTONE" or result == "CLOSED" or result == ">" or result == "COMMAND NOT SUPPORT":
                    if "ERROR" in result:
                        if cmdstr:
                            print(cmdstr.replace(self.LINE_FEED, "") +
                                  ": " + convert_to_string(self.savbuf))

                    if result == "NO CARRIER" or result == "CLOSED":
                        print(result)
                        return line

                    # Clear buffer
                    while self.ser.in_waiting:
                        self.ser.readline()

                    return line

                # Check for valid ip address
                if is_valid_ipaddress(result):
                    return line

    def grps_connect(self, profile: dict):
        """
        APN Profile
        ==========
        return
        ------
        True(bool) - Success\n
        ERROR(String) - Error Info\n
        Profile
        ---
        CID: 1 : Profile ID
        Name: internet\n
        Username: ""\n
        Password: ""\n
        APN: internet\n
        MCC (Mobile Country Code): 268 (Portugal)\n
        MNC (Mobile Network Code): 07 (NOS/Optimus)\n
        APN Type: internet
        """

        # APN Profile
        apn_cid = profile["apn_cid"]
        apn = profile["apn"]
        apn_name = profile["apn_name"]
        apn_pass = profile["apn_pass"]
        apn_type = profile["apn_type"]
        apn_ip = profile["apn_ip"]

        # Check GPRS Status
        if not self.modem.get_gprs_status():
            # Set Codification
            # +CSCS: ("GSM","HEX","IRA","PCCP","PCDN","UCS2","8859-1")
            codification = "IRA"
            if self.modem.get_codification() != codification:
                result = self.modem.set_codification(codification)
                if not result:
                    print("Fail to set codification: " + codification)
                else:
                    print("Set Codification: " + codification)

            # NOTE: to set profile, GPRS must by deactivated
            # self.modem.get_gprs_status("0")
            # -> AT+CGATT=0
            # -> +PDP: DEACT

            # Config GPRS and TCP/IP Mode

            # Enable to get details of IP address and Port number
            if not self.modem.show_remote_ip():
                self.modem.set_show_remote_ip("1")

             # Set PROFILE APN PDP Context
            apn_attr = {
                "apn_cid": apn_cid,
                "apn_address": apn_type,
                "apn": apn,
                "apn_ip": apn_ip,
            }
            result = self.modem.set_apn(apn_attr)
            if not result:
                print("Fail to Set APN Profile")
                return self.get_response()

            print("APN Profile set: Ok")

            # Attach GPRS to the APN PROFILE network
            # Activate the PDP context
            self.modem.active_profile("1")

            # Set APN Definitions
            result = self.modem.set_apn_login(apn, apn_name, apn_pass)
            if not result:
                print("Fail Setting APN")
                return self.get_response()

            print("APN Login: OK")

            # ENABLE GPRS Service
            if not self.modem.set_gprs_status("1"):
                print("Fail Enable GPRS")
                return self.get_response()

            print("GPRS Enable")

            time.sleep(1)

            # Make Connection - Bring up the wireless connection
            result = self.modem.wireless_up()
            if result:
                print("Wireless Connection: ready")

            time.sleep(2)

        return True

    def open_internet_connection(self, apn_profile: dict = None):
        """
        Open a internet connection to APN Profile
        =========================================
        """

        # APN Profile
        apn_profile = {
            "apn_cid": "1",
            "apn": "internet",
            "apn_name": "",
            "apn_pass": "",
            "apn_type": "IP",
            "apn_ip": "0.0.0.0",
        }

        # Check GPRS Status
        if not self.modem.get_gprs_status():
            result = self.grps_connect(apn_profile)
            if not result:
                return result

        # Get Ip Address
        result = self.modem.get_ip_address()
        if not is_valid_ipaddress(result):
            return result

        print("IP: " + result)
#
        # Check IP status
        result = self.mo  # dem.check_ip_address_status()
        if not result:
            return result

        return True

    def close_internet_connection(self):
        """
        Close internet connection
        ================
        - Turn off GPRS
        - Turn off APN PROFILE in PDP Context
        """
        # Deactivate PDP context and Detach GPRS
        self.modem.set_gprs_status("0")

        # bring wireless down
        self.modem.wireless_down()
        return True

    def open_tcp_connection(self, protocol: str, ip: str, port: str):
        """
        Start a TCP connection to remote address
        ----------------------------------------
        Protocol - TCP/UDP\n
        ip - IP address OR FQN\n
        Port - 80/443 is TCP\n
        """
        #cmdstr = 'AT+CIPSTART="TCP","www.energiasimples.pt","443"'
        cmdstr = 'AT+CIPSTART="{}","{}","{}"'.format(protocol, ip, port)
        self.exec(cmdstr + self.LINE_FEED, cmdstr)
        result = self.get_response().split('\r\n')  # Look for "OK" of the AT command
        value = result[0]
        # Look for "OK" on AT Command
        if value != 'OK':
            return value

        # Look for "CONNECT OK" of the TCP connection
        self.wait_answer()
        result = self.get_response().split('\r\n')
        # look for the last value
        value = result[len(result) - 1]
        if "CONNECT OK" not in value:
            return value

        print("{} connection to {} on port {}: ready".format(protocol, ip, port))
        return True

    def send_tcp_request(self, payload: str):
        # Open AT buffer in DATA MODE to send http request
        cmdstr = 'AT+CIPSEND={}'.format(len(payload) + 2)
        cmdstr = cmdstr + self.LINE_FEED
        # clean buffer
        while self.ser.in_waiting:
            self.ser.readline()
        # execute command
        self.ser.write(cmdstr.encode())
        # discard linefeed etc
        self.ser.readline()
        # wait for ">" indicator
        self.wait_answer(cmdstr)
        result = self.get_response()
        if result == ">":
            # DATA MODE ENABLE
            print(result)
            print(payload)
            # Write http request
            self.ser.write(payload.encode())

            # send http request
            cmdstr = self.CTRL_Z
            self.ser.write(cmdstr.encode())

            # look for the anwser "SEND OK"
            self.wait_answer()
            result = self.get_response().split('\r\n')
            if "OK" not in result[0]:
                return result

            print(result[0])
            print("----------------------------------")

            # QUIT DATA MODE
            # time.sleep(1)
            # cmdstr = "+++"
            # self.ser.write(cmdstr.encode())
            # time.sleep(1)

            # wait for reply
            self.wait_answer()
            self.http_request = self.get_response()
            return True

    def send_sms(self, destno, msgtext):

        # Hangup
        cmdstr = 'ATH' + self.LINE_FEED
        self.exec(cmdstr)

        print("Sending SMS ...")
        # The value 0 represents SMS PDU mode and the value 1 represents SMS TEXT mode.
        self.exec('AT+CMGF=1' + self.LINE_FEED)

        # Codification
        # +CSCS: ("GSM","HEX","IRA","PCCP","PCDN","UCS2","8859-1")
        self.exec('AT+CSCS="IRA"' + self.LINE_FEED)

        # Set Message Storage
        #  AT+CPMS="SM" Sim Card
        #  AT+CPMS="ME" GSM/GPRS modem or mobile phone
        #  AT+CPMS="MT" Both GSM/GPRS modem and mobile phone
        storage = "MT"
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
                if "OK" in result or "ERROR" in result or result == "NO CARRIER":
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

                    # clear buf
                    while self.ser.in_waiting:
                        self.ser.readline()

                    # Hangup
                    cmdstr = 'ATH' + self.LINE_FEED
                    self.exec(cmdstr)
                    print(result)
                    return line

    def read_sms(self, id, storage: str = None):
        """
        storage
        -------
        SM. It refers to the message storage area on the SIM card.

        ME. It refers to the message storage area on the GSM/GPRS modem or mobile phone. Usually its storage space is larger than that of the message storage area on the SIM card.

        MT. It refers to all message storage areas associated with the GSM/GPRS modem or mobile phone. For example, suppose a mobile phone can access two message storage areas: "SM" and "ME". The "MT" message storage area refers to the "SM" message storage area and the "ME" message storage area combined together.

        BM. It refers to the broadcast message storage area. It is used to store cell broadcast messages.

        SR. It refers to the status report message storage area. It is used to store status reports.

        TA. It refers to the terminal adaptor message storage area.
        """

        # Value 0 represents SMS PDU mode
        # Value 1 represents SMS TEXT mode
        # +CMS ERROR: 321 "Invalid Memory Index"
        # +CMS ERROR: 518 "storage type is invalid" -> AT+CMGF=1
        # AT+CPMS="ME","SM","MT"
        self.exec('AT+CMGF=1' + self.LINE_FEED)

        if storage:
            self.exec('AT+CPMS="{}"'.format(storage) + self.LINE_FEED)

        # Read Message ID
        cmdstr = 'AT+CMGR={}' + self.LINE_FEED
        lines = self.exec(cmdstr.format(id), "Reading SMS ID: {}".format(id))

        if lines <= 2:
            print("Not Found")

        message = self.get_response().split('\r\n')
        # print(message)
        # return lines
        if lines > 2:
            header = message[0].split(',')
            if len(header) > 3:
                at = header[0].split(': ')[1]

                status = at.replace('"', '')
                if isinstance(at, int):
                    statusDict = {
                        "0": "REC READ",
                        "1": "REC UNREAD",
                        "2": "STO SENT",
                        "3": "STO UNSENT",
                        "4": "ALL"
                    }
                    status = statusDict[at]

                received_from = header[1].replace('"', '')
                received_name = header[2].replace('"', '')

                received_date = header[3].replace('"', '')
                received_time = header[4].replace('"', '')

                time = received_time[0:8]
                signal = received_time[8:9]
                gmt = received_time[9:11]
                hour = int(int(gmt) * 15 / 60)
                minute = int(gmt) * 15 - hour * 60

                date_time_str = "{} {} {}{:02d}{:02d}".format(
                    received_date, time, signal, hour, minute)

                # date_time_str = '20/12/26 19:00:15 +0100'

                print(date_time_str)

                sended_at = datetime.datetime.strptime(
                    date_time_str, '%y/%m/%d %H:%M:%S %z')
                date_time = sended_at.strftime("%Y-%m-%d %H:%M:%S %Z")

                print("Status: " + status)
                print("From: " + received_from)
                if received_name != '':
                    print("Name: " + received_name)
                print("Date Time: +" + date_time)

        if lines > 3:
            message = message[1]
            print("Text: " + message)

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
                    break

                # Handle no carrier
                elif params[0] == "NO CARRIER":
                    break

                # Handle new incoming Message
                elif params[0] == "RING" or params[0][0:5] == "+CLIP":
                    # @todo handle
                    pass

                elif params[0] == "BUSY":
                    break

    def get_storages(self) -> str:
        # Set Memory Storage
        # +CPMS: ("SM","ME","SR"),("SM","ME","SR"),("SM","ME")
        cmdstr = 'AT+CPMS=?' + self.LINE_FEED
        self.exec(cmdstr)
        result = self.get_response().split('\r\n')
        stor = result[0].split(": ")[1]
        return stor

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
        self.exec(cmdstr + self.LINE_FEED, "Make a Phone Call")
        print("press 'enter' to hangup")
        input()
        self.hangup()
        print(self.get_response())

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
        """
        Get Response from AT Command
        """
        return convert_to_string(self.savbuf)

    def get_http_request(self) -> str:
        """
        Request reply
        -----------------
        TCP/UDP request or HTTP request
        """
        return self.http_request


class HSPA:

    LINE_FEED = '\r'
    RESET = 'RT'
    CTRL_Z = '\x1A'
    ESC = '\x1B'

    def __init__(self, serial_port):
        try:
            self.ser = serial.Serial(
                serial_port, baudrate=115200, timeout=1)
        except Exception as e:
            sys.exit("Error: {}".format(e))

        self._clip = None
        self._msgid = 0
        self.savbuf = None
        self.http_request = ""
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

        self.wait_answer(cmdstr)

    def wait_answer(self, cmdstr=None):
        """
        Wait for Answer
        """
        line = 0
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
                if "OK" in result or "ERROR" in result or result == "NO CARRIER" or "CONNECT" in result or result == "BUSY" or result == "NO ANSWER" or result == "NO DIALTONE" or result == "CLOSED" or result == ">" or result == "COMMAND NOT SUPPORT":
                    if "ERROR" in result:
                        if cmdstr:
                            print(cmdstr.replace(self.LINE_FEED, "") +
                                  ": " + convert_to_string(self.savbuf))

                    if result == "NO CARRIER" or result == "CLOSED":
                        print(result)
                        return line

                    # Clear buffer
                    while self.ser.in_waiting:
                        self.ser.readline()

                    return line

                # Check for valid ip address
                if is_valid_ipaddress(result):
                    return line

    def grps_connect(self, profile: dict):
        """
        APN Profile
        ==========
        return
        ------
        True(bool) - Success\n
        ERROR(String) - Error Info\n
        Profile
        ---
        CID: 1 : Profile ID
        Name: internet\n
        Username: ""\n
        Password: ""\n
        APN: internet\n
        MCC (Mobile Country Code): 268 (Portugal)\n
        MNC (Mobile Network Code): 07 (NOS/Optimus)\n
        APN Type: internet
        """

        # APN Profile
        apn_cid = profile["apn_cid"]
        apn = profile["apn"]
        apn_name = profile["apn_name"]
        apn_pass = profile["apn_pass"]
        apn_type = profile["apn_type"]
        apn_ip = profile["apn_ip"]

        # Check GPRS Status
        if not self.modem.get_gprs_status():
            # Set Codification
            # +CSCS: ("GSM","HEX","IRA","PCCP","PCDN","UCS2","8859-1")
            codification = "IRA"
            if self.modem.get_codification() != codification:
                result = self.modem.set_codification(codification)
                if not result:
                    print("Fail to set codification: " + codification)
                else:
                    print("Set Codification: " + codification)

            # NOTE: to set profile, GPRS must by deactivated
            # self.modem.get_gprs_status("0")
            # -> AT+CGATT=0
            # -> +PDP: DEACT

            # Config GPRS and TCP/IP Mode

            # Enable to get details of IP address and Port number
            if not self.modem.show_remote_ip():
                self.modem.set_show_remote_ip("1")

             # Set PROFILE APN PDP Context
            apn_attr = {
                "apn_cid": apn_cid,
                "apn_address": apn_type,
                "apn": apn,
                "apn_ip": apn_ip,
            }
            result = self.modem.set_apn(apn_attr)
            if not result:
                print("Fail to Set APN Profile")
                return self.get_response()

            print("APN Profile set: Ok")

            # Attach GPRS to the APN PROFILE network
            # Activate the PDP context
            self.modem.active_profile("1")

            # Set APN Definitions
            result = self.modem.set_apn_login(apn, apn_name, apn_pass)
            if not result:
                print("Fail Setting APN")
                return self.get_response()

            print("APN Login: OK")

            # ENABLE GPRS Service
            if not self.modem.set_gprs_status("1"):
                print("Fail Enable GPRS")
                return self.get_response()

            print("GPRS Enable")

            time.sleep(1)

            # Make Connection - Bring up the wireless connection
            result = self.modem.wireless_up()
            if result:
                print("Wireless Connection: ready")

            time.sleep(2)

        return True

    def open_internet_connection(self, apn_profile: dict = None):
        """
        Open a internet connection to APN Profile
        =========================================
        """

        # APN Profile
        apn_profile = {
            "apn_cid": "1",
            "apn": "internet",
            "apn_name": "",
            "apn_pass": "",
            "apn_type": "IP",
            "apn_ip": "0.0.0.0",
        }

        # Check GPRS Status
        if not self.modem.get_gprs_status():
            result = self.grps_connect(apn_profile)
            if not result:
                return result

        # Get Ip Address
        result = self.modem.get_ip_address()
        if not is_valid_ipaddress(result):
            return result

        print("IP: " + result)
#
        # Check IP status
        result = self.mo  # dem.check_ip_address_status()
        if not result:
            return result

        return True

    def close_internet_connection(self):
        """
        Close internet connection
        ================
        - Turn off GPRS
        - Turn off APN PROFILE in PDP Context
        """
        # Deactivate PDP context and Detach GPRS
        self.modem.set_gprs_status("0")

        # bring wireless down
        self.modem.wireless_down()
        return True

    def open_tcp_connection(self, protocol: str, ip: str, port: str):
        """
        Start a TCP connection to remote address
        ----------------------------------------
        Protocol - TCP/UDP\n
        ip - IP address OR FQN\n
        Port - 80/443 is TCP\n
        """
        #cmdstr = 'AT+CIPSTART="TCP","www.energiasimples.pt","443"'
        cmdstr = 'AT+CIPSTART="{}","{}","{}"'.format(protocol, ip, port)
        self.exec(cmdstr + self.LINE_FEED, cmdstr)
        result = self.get_response().split('\r\n')  # Look for "OK" of the AT command
        value = result[0]
        # Look for "OK" on AT Command
        if value != 'OK':
            return value

        # Look for "CONNECT OK" of the TCP connection
        self.wait_answer()
        result = self.get_response().split('\r\n')
        # look for the last value
        value = result[len(result) - 1]
        if "CONNECT OK" not in value:
            return value

        print("{} connection to {} on port {}: ready".format(protocol, ip, port))
        return True

    def send_tcp_request(self, payload: str):
        # Open AT buffer in DATA MODE to send http request
        cmdstr = 'AT+CIPSEND={}'.format(len(payload) + 2)
        cmdstr = cmdstr + self.LINE_FEED
        # clean buffer
        while self.ser.in_waiting:
            self.ser.readline()
        # execute command
        self.ser.write(cmdstr.encode())
        # discard linefeed etc
        self.ser.readline()
        # wait for ">" indicator
        self.wait_answer(cmdstr)
        result = self.get_response()
        if result == ">":
            # DATA MODE ENABLE
            print(result)
            print(payload)
            # Write http request
            self.ser.write(payload.encode())

            # send http request
            cmdstr = self.CTRL_Z
            self.ser.write(cmdstr.encode())

            # look for the anwser "SEND OK"
            self.wait_answer()
            result = self.get_response().split('\r\n')
            if "OK" not in result[0]:
                return result

            print(result[0])
            print("----------------------------------")

            # QUIT DATA MODE
            # time.sleep(1)
            # cmdstr = "+++"
            # self.ser.write(cmdstr.encode())
            # time.sleep(1)

            # wait for reply
            self.wait_answer()
            self.http_request = self.get_response()
            return True

    def send_sms(self, destno, msgtext):

        # Hangup
        cmdstr = 'ATH' + self.LINE_FEED
        self.exec(cmdstr)

        print("Sending SMS ...")
        # The value 0 represents SMS PDU mode and the value 1 represents SMS TEXT mode.
        self.exec('AT+CMGF=1' + self.LINE_FEED)

        # Codification
        # +CSCS: ("GSM","HEX","IRA","PCCP","PCDN","UCS2","8859-1")
        self.exec('AT+CSCS="IRA"' + self.LINE_FEED)

        # Set Message Storage
        #  AT+CPMS="SM" Sim Card
        #  AT+CPMS="ME" GSM/GPRS modem or mobile phone
        #  AT+CPMS="MT" Both GSM/GPRS modem and mobile phone
        storage = "MT"
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
                if "OK" in result or "ERROR" in result or result == "NO CARRIER":
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

                    # clear buf
                    while self.ser.in_waiting:
                        self.ser.readline()

                    # Hangup
                    cmdstr = 'ATH' + self.LINE_FEED
                    self.exec(cmdstr)
                    print(result)
                    return line

    def read_sms(self, id, storage: str = None):
        """
        storage
        -------
        SM. It refers to the message storage area on the SIM card.

        ME. It refers to the message storage area on the GSM/GPRS modem or mobile phone. Usually its storage space is larger than that of the message storage area on the SIM card.

        MT. It refers to all message storage areas associated with the GSM/GPRS modem or mobile phone. For example, suppose a mobile phone can access two message storage areas: "SM" and "ME". The "MT" message storage area refers to the "SM" message storage area and the "ME" message storage area combined together.

        BM. It refers to the broadcast message storage area. It is used to store cell broadcast messages.

        SR. It refers to the status report message storage area. It is used to store status reports.

        TA. It refers to the terminal adaptor message storage area.
        """

        # Value 0 represents SMS PDU mode
        # Value 1 represents SMS TEXT mode
        # +CMS ERROR: 321 "Invalid Memory Index"
        # +CMS ERROR: 518 "storage type is invalid" -> AT+CMGF=1
        # AT+CPMS="ME","SM","MT"
        self.exec('AT+CMGF=1' + self.LINE_FEED)

        if storage:
            self.exec('AT+CPMS="{}"'.format(storage) + self.LINE_FEED)

        # Read Message ID
        cmdstr = 'AT+CMGR={}' + self.LINE_FEED
        lines = self.exec(cmdstr.format(id), "Reading SMS ID: {}".format(id))

        if lines <= 2:
            print("Not Found")

        message = self.get_response().split('\r\n')
        # print(message)
        # return lines
        if lines > 2:
            header = message[0].split(',')
            if len(header) > 3:
                at = header[0].split(': ')[1]

                status = at.replace('"', '')
                if isinstance(at, int):
                    statusDict = {
                        "0": "REC READ",
                        "1": "REC UNREAD",
                        "2": "STO SENT",
                        "3": "STO UNSENT",
                        "4": "ALL"
                    }
                    status = statusDict[at]

                received_from = header[1].replace('"', '')
                received_name = header[2].replace('"', '')

                received_date = header[3].replace('"', '')
                received_time = header[4].replace('"', '')

                time = received_time[0:8]
                signal = received_time[8:9]
                gmt = received_time[9:11]
                hour = int(int(gmt) * 15 / 60)
                minute = int(gmt) * 15 - hour * 60

                date_time_str = "{} {} {}{:02d}{:02d}".format(
                    received_date, time, signal, hour, minute)

                # date_time_str = '20/12/26 19:00:15 +0100'

                print(date_time_str)

                sended_at = datetime.datetime.strptime(
                    date_time_str, '%y/%m/%d %H:%M:%S %z')
                date_time = sended_at.strftime("%Y-%m-%d %H:%M:%S %Z")

                print("Status: " + status)
                print("From: " + received_from)
                if received_name != '':
                    print("Name: " + received_name)
                print("Date Time: +" + date_time)

        if lines > 3:
            message = message[1]
            print("Text: " + message)

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
                    break

                # Handle no carrier
                elif params[0] == "NO CARRIER":
                    break

                # Handle new incoming Message
                elif params[0] == "RING" or params[0][0:5] == "+CLIP":
                    # @todo handle
                    pass

                elif params[0] == "BUSY":
                    break

    def get_storages(self) -> str:
        # Set Memory Storage
        # +CPMS: ("SM","ME","SR"),("SM","ME","SR"),("SM","ME")
        cmdstr = 'AT+CPMS=?' + self.LINE_FEED
        self.exec(cmdstr)
        result = self.get_response().split('\r\n')
        stor = result[0].split(": ")[1]
        return stor

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
        self.exec(cmdstr + self.LINE_FEED, "Make a Phone Call")
        print("press 'enter' to hangup")
        input()
        self.hangup()
        print(self.get_response())

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
        """
        Get Response from AT Command
        """
        return convert_to_string(self.savbuf)

    def get_http_request(self) -> str:
        """
        Request reply
        -----------------
        TCP/UDP request or HTTP request
        """
        return self.http_request
