from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feedback = db.Column(db.String(500), nullable=False)
    question_type = db.Column(db.String(100), nullable=False)
    team_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Feedback for {self.team_name} ({self.question_type})>'
