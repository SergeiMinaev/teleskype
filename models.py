from peewee import *


db = SqliteDatabase('teleskype.db')
db.connect(reuse_if_open=True)


class BaseModel(Model):
    class Meta:
        database = db

class Bridge(BaseModel):
    telegram_id = CharField(max_length=300)
    skype_id = CharField(max_length=300)
