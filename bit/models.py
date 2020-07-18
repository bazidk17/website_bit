from bit import db, loginman, app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@loginman.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model,UserMixin):
	id=db.Column(db.Integer,primary_key=True)
	username=db.Column(db.String(20),unique=True,nullable=False)
	email=db.Column(db.String(120),unique=True,nullable=False)
	password=db.Column(db.String(20),nullable=False)
	profile_pic=db.Column(db.String(30),nullable=False,default="default.jpg")
	posts = db.relationship('Post', backref='author', lazy=True)

	def get_reset_token(self,expires_sec=1800):
		s=Serializer(app.config["SECRET_KEY"],expires_sec)
		return s.dumps({"user_id":self.id}).decode('utf-8')

	@staticmethod ##Since it does not use self variable
	def verify_reset_token(token):
		s=Serializer(app.config["SECRET_KEY"])
		try:
			uid=s.loads(token)['user_id']
		except:
			return None
		return User.query.get(uid)

	def __repr__(self):
		return f"User('{self.username}','{self.email}')"

class Post(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	dateposted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
	title=db.Column(db.String(30),nullable=False)
	content=db.Column(db.Text,nullable=False)
	topic=db.Column(db.String(10),nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"Post('{self.title}','{self.dateposted}')"