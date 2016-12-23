from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# from models import db
# from config import basedir


app=Flask(__name__)
# app.config.from_object('config')
# db=SQLAlchemy(app)
#from app import views, models



# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://sql6150673:BhKu6fKlcg@sql6.freemysqlhosting.net/sql6150673'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql6150673:BhKu6fKlcg@sql6.freemysqlhosting.net/sql6150673'
from models import db
db.init_app(app)

from app import views, models