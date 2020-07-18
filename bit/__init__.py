from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app=Flask(__name__)
app.config['SECRET_KEY']='70599eea68b7cc55cb52c4dc6d40abb7'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///bit.db'

db=SQLAlchemy(app)
bcrypt=Bcrypt()
loginman=LoginManager(app)
loginman.login_view='login'

app.config["MAIL_SERVER"]='smtp.googlemail.com'
app.config["MAIL_PORT"]=587
app.config["MAIL_USE_TLS"]=True
app.config["MAIL_USERNAME"]='email@domain.org'#FIELD VALUE NEEDS TO BE CHANGED TO LEGIT ONES
app.config["MAIL_PASSWORD"]='password'#FIELD VALUE NEEDS TO BE CHANGED TO LEGIT ONES
mail=Mail(app)

from bit import routes