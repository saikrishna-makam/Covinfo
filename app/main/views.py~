import requests
import json
import pandas as pd
import itertools
from datetime import datetime
from flask import render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, SelectForm
from .. import db
from ..models import User, Role, Permission
from ..decorators import admin_required, permission_required


@main.route('/get_data/<state_code>', methods=['GET'])
def get_data(state_code):
    selectValue = state_code
    endpoint = "https://api.covid19india.org/states_daily.json"
    try:
        response = requests.get(endpoint)
    except requests.ConnectionError:
        return "Connection Error"
    response_text = response.text
    data = json.loads(response_text)['states_daily']
    print("Hey : " + selectValue)
    values = [data[i][selectValue] for i in range(0, len(data)) if i % 3 == 0]
    labels = [data[i]["date"] for i in range(0, len(data)) if i % 3 == 0]
        
    return jsonify({'payload':json.dumps({'values':values, 'labels':labels})})

@main.route('/', methods=['GET', 'POST'])
def index(): 
    endpoint = "https://api.covid19india.org/data.json"
    form = SelectForm()
    print(request.json)
    print()
    try:
        response = requests.get(endpoint)
    except requests.ConnectionError:
        return "Connection Error"
    response_text = response.text
    data = json.loads(response_text)
    df = pd.read_json(json.dumps(data['statewise']))
    data_total = df.iloc[0]
    legend = 'Monthly Data'
    if request.json != None:
        selectValue = request.json['state_code']
    else:
        selectValue = None
    if selectValue == None or selectValue == "None":
        timeseries_data = data['cases_time_series']
        values = [item['dailyconfirmed'] for item in timeseries_data]
        labels = [item['date'] for item in timeseries_data]
    else:
        endpoint = "https://api.covid19india.org/states_daily.json"
        try:
            response = requests.get(endpoint)
        except requests.ConnectionError:
            return "Connection Error"
        response_text = response.text
        data = json.loads(response_text)['states_daily']
        print("Hey : " + selectValue)
        values = [data[i][selectValue] for i in range(0, len(data)) if i % 3 == 0]
        labels = [data[i]["date"] for i in range(0, len(data)) if i % 3 == 0]  
        return redirect(url_for('main.get_data', state_code=selectValue))          
    return render_template('index.html', data_total = data_total, data=df, values=values, labels=labels, form=form)    
    
    
@main.route('/submit-form', methods = ['POST'])
def submitForm():
    selectValue = request.form.get('select1')
    return(str(selectValue))

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"
    

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return "For comment moderators!"
    

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)
    
    
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)
    

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
