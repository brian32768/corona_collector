#!/usr/bin/env -S conda run -n covid python
import sys
#f#rom notifications import SendNotification

#sms = SendNotification()
msg = ""
with open(0,"r") as fp:
    for line in fp.read():
        print("hi", line)
        msg += line
print(msg)
# sms.send(msg)

# cd corona_collector && ./test.py 3>&1 1>&2 2>&3 | ./send_notifications.py
