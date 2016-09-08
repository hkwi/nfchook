# coding: UTF-8
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import sessionmaker
try:
	from sqlalchemy.orm import relationship, backref
except ImportError:
	from sqlalchemy.orm import relation as relationship, backref

import sqlalchemy.ext.declarative
Base = sqlalchemy.ext.declarative.declarative_base()

def db_init(*args, **kwargs):
	engine = create_engine(*args, **kwargs)
	Base.metadata.create_all(engine)
	return sessionmaker(bind=engine)()

class Pin(Base):
	__tablename__="pin"
	tag = Column(String(255), primary_key=True)
	pin = Column(String(255)) # empty string means "open for who knows the link"
	tm = Column(DateTime)

class Hook(Base):
	__tablename__="hook"
	__table_args__ = (UniqueConstraint("tag", "url"),)
	id = Column(Integer, primary_key=True)
	tag = Column(String(255))
	url = Column(String(255))
