# About
nfchook is a set of program that triggers HTTP GET by NFC card read event.

```
 +---------+  
 |  Sony   |  USB  +-------------+  Ethernet
 | RC-S380 +-------+ RaspberryPi +------------( GET API )
 +---------+       +-------------+
```

## Setup
Install raspbian on RaspberryPi.

```bash
apt-get install python-virtualenv
virtualenv /home/pi/nfc
. /home/pi/nfc/bin/activate
pip install git+https://github.com/hkwi/nfchook
curl https://raw.githubusercontent.com/hkwi/nfchook/master/nfchook_reader.service > /etc/systemd/system/nfchook_reader.service
curl https://raw.githubusercontent.com/hkwi/nfchook/master/nfchook_web.service > /etc/systemd/system/nfchook_web.service
curl https://raw.githubusercontent.com/hkwi/nfchook/master/80-nfc.rules > /etc/udev/rules.d/80-nfc.rules
systemctl daemon-reload
systemctl enable nfchook_web
reboot
```

You don't have to start nfchook_reader because it will be start up with udev trigger. 
