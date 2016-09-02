import nfc
import datetime
import binascii
import sqlite3
import contextlib
import multiprocessing
import requests
import logging

blocker={}

long_time_ago = datetime.datetime.fromtimestamp(233431200)

urls = multiprocessing.Queue(5)

def tag_handler(tag):
	now = datetime.datetime.now()
	if now > blocker.get(tag.identifier, long_time_ago) + datetime.timedelta(seconds=2):
		tagid = binascii.b2a_hex(tag.identifier)
		db = sqlite3.connect("nfchook.db")
		db.row_factory = sqlite3.Row
		with contextlib.closing(db):
			cur = db.cursor()
			with contextlib.closing(cur):
				cur.execute("SELECT * FROM pin WHERE tag=?", (tagid,))
				pin = cur.fetchone()
				if pin is None:
					cur.execute("INSERT INTO pin(tag,tm) VALUES(?,?)", (tagid,now))
					db.commit()
				elif pin["pass"] is None:
					cur.execute("UPDATE pin SET tm=? WHERE tag=?", (now,tagid))
					db.commit()
				else:
					cur.execute("SELECT url FROM hook WHERE tag=?", (tagid,))
					for u in cur:
						urls.put(u["url"])
				
	blocker[tag.identifier] = now

def dialer(urls):
	while True:
		url = urls.get()
		try:
			requests.get(url)
		except:
			logging.error(url)

worker = multiprocessing.Process(target=dialer, args=(urls,))
worker.daemon = True
worker.start()


with nfc.ContactlessFrontend("usb") as clf:
	while True:
		clf.connect(rdwr={"on-connect": tag_handler})

