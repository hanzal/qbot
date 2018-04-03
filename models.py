import SQLAlchemy

db = SQLAlchemy()

class History(db.Model):
    """History of Questions and answers"""
    __tablename__ = "history"
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False)
    q_noun = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)

    def __init__(self, question, q_noun, answer,content):
        self.question = question
        self.q_noun = q_noun
        self.answer = answer
        self.content = content
