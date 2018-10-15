from peewee import *
from models import db

db.connect(reuse_if_open=True)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    id = CharField(max_length=300, unique=True)
    is_telegram = BooleanField()
    username = CharField(max_length=300)

class Message(BaseModel):
    user = ForeignKeyField(User)
    message = TextField()
    timestamp = TimestampField(resolution=1, utc=True)
