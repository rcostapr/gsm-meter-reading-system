#!/usr/bin/env python3
import os
import sys
import json
from serialcom.comm import COMM

print("Content-Type: application/json\n\n")

serial_port = "/dev/serial0"

method = os.environ.get("REQUEST_METHOD")
if method != 'POST':
    data = {
        "error": "Invalid access method"
    }
    print(data)
    sys.exit()

args = sys.stdin.read()
post = json.loads(args)


to = post["number"]
msg = post["message"]

phone = COMM(serial_port)
try:
    phone = COMM(serial_port)
except:
    print("Unexpected error:", sys.exc_info()[0])
    sys.exit()


# print(post)
# sys.exit()

# Verify connection
state = phone.connection_status()
if not state:
    print("No Connection")
    sys.exit()


# Setup session
print(phone.setup())

phone.send_sms(to, msg)

sys.exit()
