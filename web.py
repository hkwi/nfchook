import os
import sqlite3
import contextlib
import datetime
from beaker.middleware import SessionMiddleware
from flask import Flask, render_template, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy

from . import data

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:////tmp/nfchook.db")
db = SQLAlchemy(app)

@app.before_first_request
def setup():
	data.Base.metadata.create_all(db.engine)

@app.route("/", methods=["GET"])
def unpin_list():
	since = datetime.datetime.now() - datetime.timedelta(hours=1)
	tags = db.session.query(data.Pin).filter_by(pin=None).filter(data.Pin.tm > since).all()
	return render_template("list_unpin.html", tags=tags)

@app.route("/tag/<tagid>", methods=["GET"])
def tag_show(tagid):
	tag = db.session.query(data.Pin).filter_by(tag=tagid).first()
	
	if tag is None:
		abort(404)
	
	if tag["pin"] is None:
		return render_template("tag_init.html", tagid=tagid)
	
	session = request.environ["beaker.session"]
	if tag["pin"] and tag["pin"] != session["pin"]:
		return render_template("tag_pin.html", tagid=tagid)
	
	hooks = data.Hook.query.filter_by(tag=tagid).all()
	return render_template("tag_show.html", hooks=hooks)

@app.route("/tag/<tagid>/init", methods=["POST"])
def tag_init(tagid):
	pin = data.Pin.query.filter_by(tag=tagid, pin=None).first()
	if pin:
		pin.pin = request.params.get("pin", "")
		db.session.add(pin)
		db.session.commit()
	return redirect(url_for("tag_show", tagid=tagid))

@app.route("/tag/<tagid>/unlock", methods=["POST"])
def tag_unlock(tagid):
	pin = data.Pin.query.filter_by(tag=tagid, pin=None).first()
	if pin and request.params["pin"] == pin.pin:
		session = request.environ["beaker.session"]
		session["pin"] = pin.pin
		session.save()
	return # redirect to "/tag/<tagid>"

@app.route("/tag/<tagid>/add", methods=["POST"])
def hook_add(tagid):
	session = request.environ["beaker.session"]
	pin = data.Pin.query.filter_by(tag=tagid).first()
	if pin and pin.pin == session.get("pin"):
		hook = data.Hook()
		hook.tag = tagid
		hook.url = request.params["url"]
		db.session.add(hook)
		db.session.commit()
	return # redirect

@app.route("/tag/<tagid>/delete", methods=["POST"])
def hook_delete(tagid):
	session = request.environ["beaker.session"]
	pin = data.Pin.query.filter_by(tag=tagid).first()
	hook = data.Hook.query.filter_by(tag=tagid, url=request.params["url"]).first()
	if pin and pin.pin == session.get("pin") and hook:
		db.session.delete(hook)
		db.session.commit()
	return # redirect

def main():
	app.wsgi_app = SessionMiddleware(app.wsgi_app, {"session.type": "cookie"})
	app.run(host="")

if __name__=="__main__":
	main()

