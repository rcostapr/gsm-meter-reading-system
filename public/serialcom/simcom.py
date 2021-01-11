# coding: utf-8
# Copyright (c) rcostapr, 2020-2021
from util.function import is_valid_ipaddress


class SIMCOM():

    """
    Implement AT Communications with simcom modules for GSM and GPRS connections
    """

    def __init__(self, serial):
        self.serial = serial

    def check_connection(self) -> bool:
        """
        Check Modem Connection State
        """
        # Check connection
        if not self.active():
            return False

        # Device info
        print(self.get_device_info())

        # Get Network info
        result = self.get_cops()
        print(result["info"])

        # Get Signal
        signal = self.get_signal()
        print("Signal: " + signal["info"])

        # Phone activity status
        act = self.get_activity()
        print(act["info"])
        if int(act["value"]) != 0:
            return False

        # Vertical space
        print("")

        return True

    def setup(self) -> str:
        """
        Setup simcom module
        """
        # command echo off
        self.echo("0")

        # sets the level of functionality in the MT
        if int(self.get_cfun()) != 1:
            self.set_cfun("1")

        # caller line identification
        if int(self.get_clip()) != 1:
            self.set_clip("1")

        # Get Network info
        result = self.get_cops()
        if result["net"] and result["mode"] != "automatic":
            self.set_cops("0")

        # get Clock
        value = self.get_cclk()
        return "Setup Finished: " + value

    def active(self):
        """
        AT Command
        Check if modem responde
        """
        cmdstr = 'AT'
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0]
        if value != 'OK':
            return False
        return True

    def echo(self, value: str):
        """
        Setup AT Echo \n
        0 - Off \n
        1 - On
        """
        # command echo off
        cmdstr = 'ATE{}'.format(value)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0]
        if value != 'OK':
            return value
        return True

    def set_cfun(self, value: str):
        """
        Sets the level of functionality in the MT \n
        0 - minimum functionality \n
        1 - full functionality \n
        2 - disable phone transmit RF circuits only \n
        3 - disable phone receive RF circuits only \n
        4 - disable phone both transmit and receive RF circuits
        """
        cmdstr = 'AT+CFUN={}'.format(value)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0]
        if value != 'OK':
            return value
        return True

    def get_cfun(self) -> str:
        """
        Gets the level of functionality in the MT
        ------------------------------------------
        0 - minimum functionality \n
        1 - full functionality \n
        2 - disable phone transmit RF circuits only \n
        3 - disable phone receive RF circuits only \n
        4 - disable phone both transmit and receive RF circuits
        """
        cmdstr = 'AT+CFUN?'
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0].split(': ')[1]
        return value

    def set_clip(self, value: str):
        """
        Calling Line Identification Presentation \n
        Enables a called subscriber to get the calling line identity \n
        of the calling party when receiving a mobile terminated call. \n
        0 - enables\n
        1 - disables\n
        """
        cmdstr = 'AT+CLIP={}'.format(value)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0]
        if value != 'OK':
            return value
        return True

    def get_clip(self) -> str:
        """
        Calling Line Identification Presentation
        ------------------------------------------
        0 - enables\n
        1 - disables\n
        """
        cmdstr = 'AT+CLIP?'
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0]
        if len(value.split(': ')) > 1:
            value = value.split(': ')[1].split(",")[0]
        return value

    def set_cclk(self, value: str):
        """
        AT command sets the clock of the device. \n

        Set date and time

        Format is "yy/MM/dd,hh:mm:ss±zz", where characters indicate year (two last digits),month, day, hour, minutes, seconds and time zone

        time zone indicates the difference, expressed in quarters of an hour, between the local time and GMT; range -47...+48).

        ex. "18/03/03,05:00:00-16"
        """
        cmdstr = 'AT+CCLK={}'.format(value)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0]
        if value != 'OK':
            return value
        return True

    def get_cclk(self) -> str:
        """
        AT command gets the clock of the device. \n

        Get date and time

        Format is "yy/MM/dd,hh:mm:ss±zz", where characters indicate year (two last digits),month, day, hour, minutes, seconds and time zone
        """
        cmdstr = 'AT+CCLK?'
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0].split(': ')[1].replace('"', '')
        return value

    def get_device_info(self) -> str:
        # Device
        self.serial.exec('ATI' + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        device = message[0]

        # Manufacter
        self.serial.exec('AT+CGMI' + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        manufacter = message[0]

        # Get Simcom module capability
        self.serial.exec('AT+GCAP' + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        attr = message[0].split(': ')[1].replace('"', '')

        return "Connected to device: {} {} \n with: {}".format(manufacter, device, attr)

    def get_cops(self) -> dict:
        """
        Get information about mobile network.
        -------------------------------------
        0 automatic ( field is ignored)\n
        1 manual ( field shall be present, and optionally)\n
        2 deregister from network\n
        3 set only (for read command +COPS?), do not attempt registration/deregistration ( and fields are ignored); this value is not applicable in read command response\n
        4 manual/automatic ( field shall be present); if manual selection fails, automatic mode (=0) is entered\n

        Possible values for access technology
        --------------------------------------
        0 GSM\n
        1 GSM Compact\n
        2 UTRAN\n
        3 GSM w/EGPRS\n
        4 UTRAN w/HSDPA\n
        5 UTRAN w/HSUPA\n
        6 UTRAN w/HSDPA and HSUPA\n
        7 E-UTRAN
        """
        cmdstr = 'AT+COPS?'
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')

        if "ERROR" in result[0]:
            return {
                "net": None,
                "tecno": None,
                "mode": None,
                "info": "No SIM Card Found"
            }

        message = result[0].split(': ')[1].split(',')
        if len(message) >= 3:
            mode = message[0].strip()
            tecno = message[1].strip()
            net = message[2].strip().replace('"', '')
            if len(message) > 4:
                net += ", " + message[3].strip().replace('"', '')

            modeDict = {
                "0": "automatic",
                "1": "manual",
                "2": "deregister from network",
                "3": "set only (for read command +COPS?)",
                "4": "manual/automatic"
            }
            mode = modeDict[mode]

            tecnoDict = {
                "0": "GSM",
                "1": "GSM Compact",
                "2": "UTRAN",
                "3": "GSM w/EGPRS",
                "4": "UTRAN w/HSDPA",
                "5": "UTRAN w/HSUPA",
                "6": "UTRAN w/HSDPA and HSUPA",
                "7": "E-UTRAN",
            }
            tecno = tecnoDict[tecno]

            info = "Network: {} {} {}".format(net, tecno, mode)

            return {
                "net": net,
                "tecno": tecno,
                "mode": mode,
                "info": info
            }

        return {
            "net": None,
            "tecno": None,
            "mode": None,
            "info": "Not Connected to Network"
        }

    def set_cops(self, value: str) -> bool:
        """
        Set mobile network automatically or manually
        --------------------------------------------
        The selection is stored in the non-volatile memory during power-off.\n
        The set command parameters and their defined values are the following:\n
        \n
        mode
        -----
            0 – Automatic network selection\n
            1 – Manual network selection\n
            3 – Set <format> of +COPS read command response.\n
        format
        --------
            0 – Long alphanumeric <oper> format. Only for <mode> 3.\n
            1 – Short alphanumeric <oper> format. Only for <mode> 3 .\n
            2 – Numeric <oper> format\n
        oper
        ------
            String. Mobile Country Code (MCC) and Mobile Network Code (MNC) values. Only numeric string formats supported.
        """
        cmdstr = 'AT+COPS={}'.format(value)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')
        if "ERROR" in result[0]:
            return False
        return True

    def get_signal(self) -> dict:
        """
        Quality of Signal
        =================
        return
        ------
        {
          "value": value,
          "info": info
        }
        \n
        Value 	RSSI dBm 	Condition
        -----------------------------
        2 	    -109 	    Marginal\n
        3 	    -107 	    Marginal\n
        4 	    -105 	    Marginal\n
        5 	    -103 	    Marginal\n
        6 	    -101 	    Marginal\n
        7 	    -99 	    Marginal\n
        8 	    -97 	    Marginal\n
        9 	    -95 	    Marginal\n
        10 	    -93 	    OK\n
        11 	    -91 	    OK\n
        12 	    -89 	    OK\n
        13 	    -87 	    OK\n
        14 	    -85 	    OK\n
        15 	    -83 	    Good\n
        16 	    -81 	    Good\n
        17 	    -79 	    Good\n
        18 	    -77 	    Good\n
        19 	    -75 	    Good\n
        20 	    -73 	    Excellent\n
        21 	    -71 	    Excellent\n
        22 	    -69 	    Excellent\n
        23 	    -67 	    Excellent\n
        24 	    -65 	    Excellent\n
        25 	    -63 	    Excellent\n
        26 	    -61 	    Excellent\n
        27 	    -59 	    Excellent\n
        28 	    -57 	    Excellent\n
        29 	    -55 	    Excellent\n
        30 	    -53 	    Excellent\n
        """
        self.serial.exec('AT+CSQ' + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0].split(':')[1].strip().split(',')[0]

        signalDict = {
            "0": "No Signal",
            "1": "No Signal",
            "2": "Very Week",
            "3": "Very Week",
            "4": "Very Week",
            "5": "Very Week",
            "6": "Very Week",
            "7": "Very Week",
            "8": "Very Week",
            "9": "Very Week",
            "10": "Week",
            "11": "Week",
            "12": "Week",
            "13": "Week",
            "14": "Week",
            "15": "Good",
            "16": "Good",
            "17": "Good",
            "18": "Good",
            "19": "Good",
            "20": "Excellent",
            "21": "Excellent",
            "22": "Excellent",
            "23": "Excellent",
            "24": "Excellent",
            "25": "Excellent",
            "26": "Excellent",
            "27": "Excellent",
            "28": "Excellent",
            "29": "Excellent",
            "30": "Excellent",
        }
        info = signalDict[value]
        return {
            "value": value,
            "info": info
        }

    def get_activity(self) -> str:
        """
        Phone activity status
        =====================
        return
        ------
        {
          "value": value,
          "info": info
        }\n
        0 ready\n
        1 unavailable\n
        2 unknown\n
        3 ringing\n
        4 call in progress\n
        5 asleep\n
        """
        self.serial.exec('AT+CPAS' + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0].split(':')[1].strip()
        cpasDict = {
            '0': "ready",
            '1': "unavailable",
            '2': "unknown",
            '3': "ringing",
            '4': "call in progress",
            '5': "asleep",
        }
        result = cpasDict[value]
        return {
            "value": value,
            "info": result
        }

    def set_apn(self, apn: dict) -> str:
        """
        Set APN PROFILE in PDP Context
        ----------------------------------
        PDP (Packet Data Protocol)  addresses can be X.25, IP, or both
        """
        # APN Attr
        apn_cid = 1
        apn_type = "IP"
        apn = "internet"
        apn_ip = "0.0.0.0"
        apn_data_compression = 0
        apn_header_compression = 0

        cmdstr = 'AT+CGDCONT={},"{}","{}","{}",{},{}'.format(
            apn_cid, apn_type, apn, apn_ip, apn_data_compression, apn_header_compression)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')
        return result[0]

    def get_apn(self) -> str:
        """
        GET APN PROFILE in PDP Context
        ----------------------------------
        PDP (Packet Data Protocol)  addresses can be X.25, IP, or both
        """
        cmdstr = 'AT+CGDCONT?'
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response()
        return result

    def get_gprs_status(self) -> bool:
        """
        GET Packet Domain Service status
        =====================
        0 - Detach
        1 - Attach
        ------
        """
        cmdstr = "AT+CGATT?"
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0].split(": ")[1]
        if value != '1':
            return False
        return True

    def set_gprs_status(self, state: str) -> bool:
        """
        SET Packet Domain Service status
        =====================
        0 - Detach
        1 - Attach
        ------
        """
        cmdstr = "AT+CGATT={}".format(state)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response()
        if 'OK' not in message:
            # Show Profiles
            print(self.get_apn())
            # Show Active Profiles
            print(self.get_profile())
            return False
        return True

    def get_profile(self) -> bool:
        """
        GET PDP context
        =====================
        Syntax:
        ------
        +CGACT=state,cid\n
        The set command parameters and their defined values are the following:\n

        state
        -----
            0 – Deactivate\n
            1 – Activate\n
        cid
        ---
            1–11\n
        """
        cmdstr = "AT+CGACT?"
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response()
        return message

    def active_profile(self, profile: str) -> bool:
        """
        Activate the PDP context
        =====================
        profile ID \n
        Syntax:
        ------
        +CGACT=state,cid\n
        The set command parameters and their defined values are the following:\n

        state
        -----
            0 – Deactivate\n
            1 – Activate\n
        cid
        ---
            1–11\n
        """
        cmdstr = "AT+CGACT=1,{}".format(profile)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0]
        if value != 'OK':
            return False
        return True

    def inactive_profile(self, profile: str) -> bool:
        """
        Deactivate the PDP context
        =====================
        profile ID \n
        Syntax:
        ------
        +CGACT=state,cid\n
        The set command parameters and their defined values are the following:\n

        state
        -----
            0 – Deactivate\n
            1 – Activate\n
        cid
        ---
            1–11\n
        """
        cmdstr = "AT+CGACT=0,{}".format(profile)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        message = self.serial.get_response().split('\r\n')
        value = message[0]
        if value != 'OK':
            return False
        return True

    def show_remote_ip(self) -> bool:
        """
        Show Remote IP Address and Port
        -------------------
        Status for get details of IP address
        helps to add IP header in the format "+IPD (data length): payload"
        """
        cmdstr = 'AT+CIPSRIP?'
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')
        # Look for "+CIPSRIP: 0/1" of the AT command
        value = result[0].split(": ")

        if value == '0':
            return False

        return True

    def set_show_remote_ip(self, state) -> bool:
        """
        Enable or Disable to get details of IP address
        -------------------
        Show or Hide Remote IP Address and Port number\n
        0 - disable \n
        1 - enable
        """
        cmdstr = 'AT+CIPSRIP={}'.format(state)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')
        # Look for "OK" of the AT command
        value = result[0]

        if value != 'OK':
            return False

        return True

    def set_dns(self, primary: str, secondary: str) -> bool:
        """
        Configure Domain Name Server (primary DNS, secondary DNS)
        -----------------------------------------------
        primary - valid IP address
        secondary - valid IP address
        """
        if not is_valid_ipaddress(primary):
            print("Invalid IP address: " + primary)
            return False
        if not is_valid_ipaddress(secondary):
            print("Invalid IP address: " + secondary)
            return False

        cmdstr = 'AT+CDNSCFG="{}","{}"'.format(primary, secondary)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')
        if result[0] != "OK":
            return False
        return True

    def set_apn_login(self, apn: str, username: str, password: str) -> bool:
        """
        Set APN Login Definitions
        -------------------
        apn - APN name where to connect
        username - username to login
        password - password to login
        +CME ERROR: 765 -> "invalid input value"
        """
        cmdstr = 'AT+CSTT="{}","{}","{}"'.format(apn, username, password)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')
        if result[0] != "OK":
            return False
        return True

    def wireless_down(self) -> bool:
        """
        bring wireless down
        -------------------
        close the GPRS PDP context.
        """
        cmdstr = 'AT+CIPSHUT'
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')
        # Look for "OK" of the AT command
        value = result[0]

        if value != 'SHUT OK':
            print("AT+CIPSHUT: " + value)
            return False

        print(value)
        return True

    def wireless_up(self) -> bool:
        """
        Make wireless Connection
        ------------------------
        Bring up the wireless connection
        """
        self.serial.exec('AT+CIICR' + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')
        if result[0] != "OK":
            return False
        return True

    def power_down(self) -> bool:
        """
        Turn Device Off
        -------------------
        - Not Possible to turn ON via AT Command. \n
        - Only the power supply for the RTC is remained. \n
        - Software is not active. \n
        - The serial port is not accessible. \n
        - Power supply (connected to VBAT) remains applied.
        """
        cmdstr = "AT+CPOWD=1"
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')
        # Look for "OK" of the AT command
        value = result[0]

        if value != 'OK':
            return False

        print("Device Shutdown")
        return True

    def set_codification(self, codification: str) -> bool:
        """
        Set Codification
        ---------
        +CSCS: ("GSM","HEX","IRA","PCCP","PCDN","UCS2","8859-1")
        """
        cmdstr = 'AT+CSCS="{}"'.format(codification)
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response()
        # Look for "OK" of the AT command
        if 'OK' not in result:
            return False
        return True

    def get_codification(self) -> str:
        """
        Get Codification
        ---------
        +CSCS: ("GSM","HEX","IRA","PCCP","PCDN","UCS2","8859-1")
        """
        cmdstr = 'AT+CSCS?'
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')
        value = result[0].split(": ")[1].replace('"', '')
        return value

    def get_ip_address(self):
        """
        Gets the dynamic IP address of local
        ---------------------------
        module as allotted by GPRS network\n
        NOTE: GPRS must by activated and connected to profile
        """
        cmdstr = 'AT+CIFSR'
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')
        if "ERROR" in result[0]:
            # Turn off
            print('Fail to get IP address: ' + result[0])
            # Deactivate PDP context and Detach GPRS
            self.set_gprs_status("0")
            # bring wireless down
            self.wireless_down()
            return result
        return result[0]

    def check_ip_address_status(self):
        """
        Check dynamic IP address status
        ---------------------------
        merror STATE: PDP DEACT <- PDP Context not activated\n
        NOTE: must return "STATE: IP STATUS" for connection
        """
        cmdstr = 'AT+CIPSTATUS'
        self.serial.exec(cmdstr + self.serial.LINE_FEED)
        result = self.serial.get_response().split('\r\n')
        if "ERROR" in result[0]:
            # Turn off
            print('Fail Check dynamic IP address status: ' + result[0])
            # Deactivate PDP context and Detach GPRS
            self.set_gprs_status("0")
            # bring wireless down
            self.wireless_down()
            return result
        return True
