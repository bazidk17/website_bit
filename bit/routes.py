from bit import app,db,bcrypt,loginman,mail
from flask import render_template,redirect,url_for,flash,request,abort
from bit.forms import RegisterForm,LoginForm,UpdateProfileForm,PostForm,resetRequestForm,resetPasswordForm
from bit.models import User,Post
from flask_login import login_user,current_user,logout_user,login_required
import secrets
import os
from PIL import Image
from flask_mail import Message


def save_picture(mypic):
	random=secrets.token_hex(4)
	f_name,f_ext=os.path.split(mypic.filename)
	newname_pic=random+f_ext
	picture_path=os.path.join(app.root_path,'static/Profile',newname_pic)

	i=Image.open(mypic)
	
	output_size=(250,250)
	i.thumbnail(output_size)
	i.save(picture_path)
	return newname_pic


@app.route("/")
@app.route("/home")
def home():
	pages=request.args.get('page',1,type=int)
	posts=Post.query.order_by(Post.dateposted.desc()).paginate(page=pages,per_page=4)
	return render_template("homepage.html",display_info=posts,topic="all")

@app.route("/home/<info_to_display>")
def filter_home(info_to_display):
	pages=request.args.get('page',1,type=int)
	posts=Post.query.filter_by(topic=info_to_display).order_by(Post.dateposted.desc()).paginate(page=pages,per_page=4)
	return render_template("homepage.html",display_info=posts,topic=info_to_display)

@app.route("/about")
def about():
	return render_template("about.html",title="About")

@app.route("/login",methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	login_form=LoginForm()
	if login_form.validate_on_submit():
		check_user=User.query.filter_by(email=login_form.txtEmail.data).first()
		if check_user and bcrypt.check_password_hash(check_user.password,login_form.txtPassword.data):
			login_user(check_user)
			nextpage=request.args.get('next')
			if nextpage:
				return redirect(nextpage)
			else:
				return redirect(url_for('home'))
		else:
			flash("Login Unsuccessful. Please check email and password","danger")

	return render_template('login.html',title="Login", form_content=login_form)

@app.route("/register",methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	regi_form=RegisterForm()
	if regi_form.validate_on_submit():
		hash_pw=bcrypt.generate_password_hash(regi_form.txtPassword.data).decode('utf-8')
		user=User(username=regi_form.txtUsername.data,email=regi_form.txtEmail.data,password=hash_pw)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created!  You are now able to log in','success')
		return redirect(url_for('login'))

	
	return render_template("register.html",title="Register",form_content=regi_form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route("/account",methods=['GET','POST'])
@login_required
def account():
	update_form=UpdateProfileForm()

	if update_form.validate_on_submit():
		if update_form.imgProfilePic.data:
			filePic=save_picture(update_form.imgProfilePic.data)
			current_user.profile_pic=filePic
		current_user.username=update_form.txtUsername.data
		current_user.email=update_form.txtEmail.data
		db.session.commit()
		flash("Your account has been updated!","success")
		return redirect(url_for('account'))
	elif (request.method=='GET'):
		update_form.txtUsername.data=current_user.username
		update_form.txtEmail.data=current_user.email	
	myimage=url_for("static",filename="Profile/"+current_user.profile_pic)
	return render_template("account.html",update_info=update_form, image_pass=myimage)

@app.route("/post/new",methods=['GET','POST'])
@login_required
def newPost():
	post_form=PostForm()
	
	if post_form.validate_on_submit():
		new_post_content=Post(title=post_form.txtTitle.data,content=post_form.txtContent.data,author=current_user,topic=post_form.ddTopic.data)
		db.session.add(new_post_content)
		db.session.commit()
		flash("Your post has been created","success")
		return redirect(url_for("home"))
	return render_template("new_post.html",title="New Post",form_content=post_form)

@app.route("/post/<int:post_id>")
def post(post_id):
	selected_post=Post.query.get_or_404(post_id)
	return render_template("post.html",title=selected_post.title,post=selected_post)

@app.route("/post/<int:post_id>/update",methods=['GET','POST'])
@login_required
def update_post(post_id):
	selected_post=Post.query.get_or_404(post_id)
	if selected_post.author!=current_user:
		abort(403)
	post_form=PostForm()
	if post_form.validate_on_submit():
		selected_post.title=post_form.txtTitle.data
		selected_post.content=post_form.txtContent.data
		db.session.commit()
		flash('Your post has been updated!','success')
		return redirect(url_for("post",post_id=selected_post.id))
	elif request.method=="GET":
		post_form.txtTitle.data=selected_post.title
		post_form.txtContent.data=selected_post.content
	return render_template("new_post.html",title="Update Post", form_content=post_form)

@app.route("/post/<int:post_id>/delete",methods=['GET','POST'])
def delete_post(post_id):
	selected_post=Post.query.get_or_404(post_id)
	if selected_post.author!=current_user:
		abort(403)
	db.session.delete(selected_post)
	db.session.commit()
	flash("Post has beeen deleted","success")
	return redirect(url_for('home'))


def send_email(user):
	certain_token=user.get_reset_token()
	message=Message('Password Reset Request',sender='norepely@demo.com',recipients=[user.email])
	message.body=f'''To reset Password visit the following link
{url_for('reset_password',token=certain_token,_external=True)}

If you did not make this request then ignore this email.
'''
	mail.send(message)

@app.route("/reset_password",methods=['GET','POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	requestForm=resetRequestForm()
	if requestForm.validate_on_submit():
		selected_user=User.query.filter_by(email=requestForm.txtEmail.data).first()
		send_email(selected_user)
		flash("User has been sent an email with instructions to reset your Password","info")
		return redirect(url_for('login'))
	return render_template("request_reset.html",form_content=requestForm,title="Reset Password")

@app.route("/reset_password/<token>",methods=['GET','POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user=User.verify_reset_token(token)
	if user is None:
		flash("That is an invalid or expired token","warning")
		return redirect(url_for('reset_request'))
	passwordForm=resetPasswordForm()
	if passwordForm.validate_on_submit():
		hash_pw=bcrypt.generate_password_hash(passwordForm.txtPassword.data).decode('utf-8')
		user.password=hash_pw
		db.session.commit()
		flash('Your password has been updated! You are now able to log in','success')
		return redirect(url_for('login'))
	return render_template("password_reset.html",form_content=passwordForm,title="Reset Password")
