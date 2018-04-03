from peewee import *
db = SqliteDatabase('qbot.db')

class History(Model):
    """History of Questions and answers"""
    question = CharField()
    q_noun = CharField()
    answer = CharField()

    class Meta:
        database = db



db.create_tables([History])
