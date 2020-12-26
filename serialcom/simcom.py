# coding: utf-8
# Copyright (c) rcostapr, 2020-2021
# Open-source software, see LICENSE file for details


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
        value = message[0].split(': ')[1].split(",")[0]
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
        self.exec(cmdstr + self.LINE_FEED)
        result = self.get_response().split('\r\n')
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
