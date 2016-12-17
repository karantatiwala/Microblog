from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class users(db.Model):
    __tablename__ = 'users'
    username=db.Column(db.String(50),unique=True, primary_key=True)
    password=db.Column(db.String(50),unique=True)


    def __init__(self, username,password):
        self.username = username
        self.password = password

class post(db.Model):
    __tablename__ = 'post'
    id=db.Column(db.Integer,primary_key=True)
    post=db.Column(db.String(500), nullable=False) 
    title=db.Column(db.String(100), nullable=False)
    tags=db.Column(db.String(100), nullable=False)
    date_time=db.Column(db.DateTime(100), nullable=True)
    userid=db.Column(db.String(25), nullable=False)

    def __init__(self, post,title,tags,userid):
        # self.id = id
        self.post = post
        self.title = title
        self.tags = tags
        self.userid = userid
        # self.date_time = date_time