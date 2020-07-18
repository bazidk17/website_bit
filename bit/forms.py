from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from bit.models import User
from flask_login import current_user

class LoginForm(FlaskForm):
	txtEmail=StringField("Email",validators=[DataRequired(),Email()])
	txtPassword=PasswordField("Password",validators=[DataRequired(),Length(min=6)])
	btnLogin=SubmitField("Log In")


class RegisterForm(FlaskForm):
	txtUsername=StringField("Username",validators=[DataRequired(),Length(min=2,max=20)])
	txtEmail=StringField("Email",validators=[DataRequired(), Email()])
	txtPassword=PasswordField("Password",validators=[DataRequired(),Length(min=6,max=20)])
	txtConfirm_Pass=PasswordField("Confirm Password",validators=[DataRequired(),EqualTo('txtPassword')])
	btnRegister=SubmitField("Register")

	def validate_txtUsername(self,txtUsername):
		temp=User.query.filter_by(username=txtUsername.data).first()
		if temp:
			raise ValidationError('That username is already taken. Please choose another username.')
	def validate_txtEmail(self,txtEmail):
		temp=User.query.filter_by(email=txtEmail.data).first()
		if temp:
			raise ValidationError('That email is already registered.')

class UpdateProfileForm(FlaskForm):
	txtUsername=StringField("Username",validators=[DataRequired(),Length(min=2,max=20)])
	txtEmail=StringField("Email",validators=[DataRequired(), Email()])
	imgProfilePic=FileField("Picture",validators=[FileAllowed(["jpg","png"])])
	btnUpdate=SubmitField("Update")

	def validate_txtUsername(self,txtUsername):
		if (txtUsername.data!=current_user.username):
			temp=User.query.filter_by(username=txtUsername.data).first()
			if temp:
				raise ValidationError("That username is already taken. Please choose another username.")

	def validate_txtEmail(self,txtEmail):
		if (txtEmail.data!=current_user.email):
			temp=User.query.filter_by(email=txtEmail.data).first()
			if temp:
				raise ValidationError("This email is already registered.")

class PostForm(FlaskForm):
	txtTitle=StringField("Title",validators=[DataRequired()])
	txtContent=TextAreaField("Content",validators=[DataRequired()])
	ddTopic=SelectField("Topic",choices=[('----','----'),('Food','Food'),('Sports','Sports'),('Cars','Cars'),('Weather','Weather')],validators=[DataRequired()],default="0")
	btnPost=SubmitField("Post")

	def validate_ddTopic(self,ddTopic):
		if ddTopic.data=="----":
			raise ValidationError()	##Just raises error

class resetRequestForm(FlaskForm):
	txtEmail=StringField("Email",validators=[DataRequired(),Email()])
	btnRequest=SubmitField("Request Password Reset")

	def validate_txtEmail(self,txtEmail):
		temp=User.query.filter_by(email=txtEmail.data).first()
		if temp is None:
			raise ValidationError("Email has not been registered. Please register using this email.")

class resetPasswordForm(FlaskForm):
	txtPassword=PasswordField("Password",validators=[DataRequired(),Length(min=6,max=20)])
	txtConfirm_Pass=PasswordField("Confirm Password",validators=[DataRequired(),EqualTo('txtPassword')])
	btnApply=SubmitField("Update Password")