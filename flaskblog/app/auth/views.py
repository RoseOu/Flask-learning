from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import logout_user, login_required, login_user, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetForm
from .. import db


@auth.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid username or password.')
	return render_template('auth/login.html', form=form)

@auth.route('/logout', methods=['GET','POST'])
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET','POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data, username=form.username.data, password=form.password.data)
		db.session.add(user)
		flash('You can now login.')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html', form=form)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			flash('Your password has been changed.')
			return redirect(url_for('main.index'))
		else:
			flash('Invalid password.')
	return render_template("auth/change_password.html", form=form)

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset():
    form = PasswordResetForm()
    if form.validate_on_submit():
    	user1 = User.query.filter_by(email=form.email.data).first()
    	user2 = User.query.filter_by(username=form.username.data).first()
        if user1 is not None and user2 is not None and user1 == user2:
        	user1.password = form.password.data
        	db.session.add(user1)
        	flash('Your password has been reseted.')
        	return redirect(url_for('auth.login'))
        else:
        	flash('Invalid Email or username.')
    return render_template('auth/reset_password.html', form=form)

