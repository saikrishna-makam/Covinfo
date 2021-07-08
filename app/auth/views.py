from flask import render_template, redirect, request, url_for, flash, current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm


@auth.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        user = User(email=register_form.email.data, username=register_form.username.data, password=register_form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        app.logger.debug('User confirmation token: ' + str(token))
        send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        app.logger.info('A confirmation email has been sent to user by email.')
        return redirect(url_for('covinfo.index'))
    return render_template('auth/register.html', form=register_form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    app.logger.debug('Confirmation token sent through email: ' + str(token))
    if current_user.confirmed:
        return redirect(url_for('covinfo.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
        app.logger.info('User account is confirmed.')
    else:
        flash('The confirmation link is invalid or has expired.')
        app.logger.error('The confirmation link is invalid or has expired.')
    return redirect(url_for('covinfo.index'))
    
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    app.logger.debug('User confirmation token: ' + str(token))
    send_email(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    app.logger.info('User requested new confirmation email.')
    return redirect(url_for('covinfo.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated :
        current_user.ping()
        if not current_user.confirmed \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))
        

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('covinfo.index'))
    app.logger.warning('User has not yet confirmed their account.')
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        app.logger.debug('User Email id: ' + str(login_form.email.data) + 'Remember me: ' + str(login_form.remember_me.data))
        user = User.query.filter_by(email=login_form.email.data.lower()).first()
        if user is not None and user.verify_password(login_form.password.data):
            login_user(user, login_form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('covinfo.index')
            return redirect(next)
        flash('Invalid username or password.')
        app.logger.warning('User entered invalid username or password.')
    return render_template('auth/login.html', form=login_form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    app.logger.info('User has been logged out')
    return redirect(url_for('covinfo.index'))
    
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('covinfo.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        app.logger.debug('User Email id: ' + str(form.email.data))
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            app.logger.debug('User confirmation token: ' + str(token))
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token)
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        app.logger.info('Reset password email has been sent to user.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('covinfo.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        app.logger.debug('User password: ' + str(form.password.data))
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            app.logger.info('User password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('covinfo.index'))
    return render_template('auth/reset_password.html', form=form)
   
