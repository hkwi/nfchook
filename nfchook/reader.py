import os
import nfc
import datetime
import binascii
import contextlib
import multiprocessing
import requests
import logging

from . import data

blocker={}

long_time_ago = datetime.datetime.fromtimestamp(233431200)

urls = multiprocessing.Queue(5)

class TagHandler(object):
	def __init__(self, session):
		self.session = session
	
	def __call__(self, tag):
		logging.info(tag)
		now = datetime.datetime.now()
		if now > blocker.get(tag.identifier, long_time_ago) + datetime.timedelta(seconds=2):
			tagid = binascii.b2a_hex(tag.identifier)
			
			pin = self.session.query(data.Pin).filter_by(tag=tagid).first()
			if pin is None:
				pin = data.Pin()
				pin.tag = tagid
				pin.tm = now
				self.session.add(pin)
				self.session.commit()
			elif pin.pin is None:
				pin.tm = now
				self.session.add(pin)
				self.session.commit()
			else:
				for hook in self.session.query(data.Hook).filter_by(tag=tagid):
					urls.put(hook.url)
		blocker[tag.identifier] = now

def dialer(urls):
	while True:
		url = urls.get()
		try:
			requests.get(url)
		except:
			logging.error(url)

def main():
	logging.basicConfig(level=logging.INFO)
	dbpath = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:////tmp/nfchook.db")
	worker = multiprocessing.Process(target=dialer, args=(urls,))
	worker.daemon = True
	worker.start()
	with nfc.ContactlessFrontend("usb") as clf:
		session = data.db_init(dbpath)
		while True:
			clf.connect(rdwr={"on-connect": TagHandler(session)})

if __name__=="__main__":
	main()

