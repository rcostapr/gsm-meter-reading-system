# Smart and Intelligent GSM based Automatic Meter Reading System

-   enable_uart=1
-   dtoverlay=pi3-miniuart-bt

Automatic system to perform communication with energy smart meters for reading energy consumption or energy production

## Python Base Library

Used to perform communication with serial port

## Devices

-   Modem ZTE MF626
-   MODEM ZTE MF192
-   Raspberry Pi with GSM SIM800L Add-on

## AT Commands

-   lsof /dev/ttyACM0

### To list the running process id.then use below command

-   ps -ef | grep ttyACM0

### To list the number of running process id.then, use below commands

-   ps -ef | grep ttyACM0 | wc -l

### Determine whether the tty is currently handling any processes by typing the following:

-   ps -lt ttyACM0

### clear any process

This will clear any process that can be found running on the port and display the PID. If the tty is still unusable, continue to the next step.

-   fuser -k /dev/ttyACM0

### flush outgoing data from the port

-   ls -al /dev/ttyACM0
    Your results should look similar to the following:

crw-rw---- 1 root dialout 166, 0 dez 24 10:33 /dev/ttyACM0

This indicates that tty0 has a major device number of 166 and a minor device number of 0. Specify these numbers when using the strreset command as follows:

-   /usr/sbin/strreset -M 166 -m 0

## QT

-   cd /usr/lib/x86_64-linux-gnu/qt5/bin/
-   ./designer
-   pyuic5 gui/main.ui -0 gui/main.py
-   pyside2-uic gui/main.ui -o gui/main.py

### No package 'Qt5Svg' found ubuntu

-   sudo apt install libqt5svg5-dev

### Could not find Boost

-   sudo apt install libboost-dev
-   sudo apt install libboost-all-dev

## Apache2

-   sudo a2enmod mpm_prefork cgi
-   a2enmod rewrite
-   sudo nano /etc/apache2/sites-enabled/000-default.conf
    """
    <Directory /var/www/html>
    Options +ExecCGI -Indexes
    AddHandler cgi-script .cgi .py
    AllowOverride All
    Require all granted
    </Directory>
    """
-   systemctl restart apache2
-   sudo chmod 755 gsm.py

    """

               # Configure Domain Name Server (primary DNS, secondary DNS)
               # self.modem.set_dns("4.4.4.4", "8.8.8.8")

               AT+CDNSCFG="4.4.4.4","8.8.8.8"
               AT+CDNSCFG="8.8.8.8","8.8.4.4"
               AT+CDNSCFG=?
               +CDNSCFG: ("Primary DNS"),("Secondary DNS")

               GET / HTTP/1.1\r\nHost: www.energiasimples.pt\r\nAccept: text/html, application/xhtml+xml, application/xml; q = 0.9, image/webp, _/_; q = 0.8\r\nConnection: keep-alive

               GET / HTTP/1.1\nUser-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv: 84.0) Gecko/20100101 Firefox/84.0\n\nHost: www.energiasimples.pt\nAccept: text/html, application/xhtml+xml, application/xml; q = 0.9, image/webp, _/_; q = 0.8\n\Accept-Language: en-us\nConnection: Keep-Alive

               AT+CIPSTART = "SSL", "iot.espressif.cn", 8443
               AT+CIPSTART = "SSL", "192.168.101.110", 1000, , "192.168.101.100"

               AT+CIPSEND
               >
               GET https: // www.m2msupport.net/m2msupport/http_get_test.php HTTP/1.0

               GET / HTTP/1.1
               CTRL+Z

               GET / HTTP/1.1
               Host: 85.234.128.80
               User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv: 84.0) Gecko/20100101 Firefox/84.0
               Accept: text/html, application/xhtml+xml, application/xml; q = 0.9, image/webp, */*; q = 0.8
               Accept-Language: en-US, en; q = 0.5
               Accept-Encoding: gzip, deflate, br
               DNT: 1
               Connection: keep-alive
               Upgrade-Insecure-Requests: 1
               Cache-Control: max-age = 0
               TE: Trailers

               PUT / somewhere/fun HTTP/1.1
               Host: origin.example.com
               Content-Type: video/h264
               Content-Length: 1234567890987
               Expect: 100-continue

               POST / HTTP/1.1
               Host: foo.com
               Content-Type: application/x-www-form-urlencoded
               Content-Length: 13

               say = Hi & to = Mom

               GET / www.energiasimples.pt HTTP/1.1
               User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
               Host: www.energiasimples.pt
               Accept-Language: en-us
               Accept-Encoding: gzip, deflate
               Connection: Keep-Alive

               POST / cgi-bin/process.cgi HTTP/1.1
               User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
               Host: www.tutorialspoint.com
               Content-Type: application/x-www-form-urlencoded
               Content-Length: length
               Accept-Language: en-us
               Accept-Encoding: gzip, deflate
               Connection: Keep-Alive

               licenseID = string & content = string & /paramsXML = string

               POST / cgi-bin/process.cgi HTTP/1.1
               User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
               Host: www.tutorialspoint.com
               Content-Type: text/xml; charset = utf-8
               Content-Length: length
               Accept-Language: en-us
               Accept-Encoding: gzip, deflate
               Connection: Keep-Alive

               <?xml version = "1.0" encoding = "utf-8"?>
               <string xmlns = "http://clearforest.com/" > string < /string >

               POST
               Host: ********connected.com
               Accept: application/json
               Content-Length: 224
               Content-Type: application/jsonr
               {"email": "myemail.com", "password": "myPassword"}

               """

""" # Start a TCP connection to remote address. Port 80/443 is TCP.
cmdstr = 'AT+CIPSTART="TCP","www.energiasimples.pt","443"'
self.exec(cmdstr + self.LINE_FEED, cmdstr)
result = self.get_response().split('\r\n') # Look for "OK" of the AT command
value = result[0]
if value != 'OK':
return "value"

        # Look for "CONNECT OK" of the TCP connection
        self.wait_answer()
        result = self.get_response().split('\r\n')
        # look for the last value
        value = result[len(result) - 1]
        if "CONNECT OK" not in value:
            return value

        print(value)
        """

        payload = """GET / HTTP/1.1

User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86*64; rv:84.0) Gecko/20100101 Firefox/84.0
Host: www.energiasimples.pt
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/\_;q=0.8
Accept-Language: en-us
Connection: Keep-Alive"""

        # Open AT buffer in DATA MODE to send http request
        # cmdstr = 'AT+CIPSEND={}'.format(len(payload) + 2)
        """
        cmdstr = 'AT+CIPSEND'
        print(cmdstr)
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
            time.sleep(1)
            cmdstr = "+++"
            self.ser.write(cmdstr.encode())
            time.sleep(1)

            # wait for request reply
            self.wait_answer()
            self.http_request = self.get_response()
        """
