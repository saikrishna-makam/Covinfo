import requests
import json
import itertools
from datetime import datetime
from flask import render_template, make_response, request, jsonify, session, redirect, url_for, flash
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, SelectForm
from .. import db
from ..models import User, Role, Covid, Timeseries, Permission
from ..decorators import admin_required, permission_required

def fetch_api():
    states = ['an', 'ap', 'ar', 'as', 'br', 'ch', 'ct', 'dd', 'dl', 'dn', 'ga', 'gj', 'hp', 'hr', 'jh', 'jk', 'ka', 'kl', 
              'la', 'ld', 'mh', 'ml', 'mn', 'mp', 'mz', 'nl', 'or', 'pb', 'py', 'rj', 'sk', 'tg', 'tn', 'up', 'ut', 'wb']

    endpoint1 = "https://api.covid19india.org/data.json"
    endpoint2 = "https://api.covid19india.org/states_daily.json"
    
    try:
        response1 = requests.get(endpoint1)
        response2 = requests.get(endpoint2)
    except requests.ConnectionError:
        return "Connection Error"
    response_text1 = response1.text
    response_text2 = response2.text
    data1 = json.loads(response_text1)
    data2 = json.loads(response_text2)['states_daily']

    statewise_data = data1['statewise']
    timeseries_data = data1["cases_time_series"]
    for state in statewise_data:
        if state['statecode'].lower() == 'tt':
            covid = Covid(state=state['state'], confirmed=state['confirmed'], 
                          active=state['active'], recovered=state['recovered'], 
                          deaths=state['deaths'], deltaconfirmed=timeseries_data[len(timeseries_data) - 1]['dailyconfirmed'], 
                          deltarecovered=timeseries_data[len(timeseries_data) - 1]['dailyrecovered'], deltadeaths=timeseries_data[len(timeseries_data) - 1]['dailydeceased'],
                          state_code=state['statecode'].lower())
        else:
            covid = Covid(state=state['state'], confirmed=state['confirmed'], 
                          active=state['active'], recovered=state['recovered'], 
                          deaths=state['deaths'], deltaconfirmed=data2[len(data2) - 3][state['statecode'].lower()], 
                          deltarecovered=data2[len(data2) - 2][state['statecode'].lower()], deltadeaths=data2[len(data2) - 1][state['statecode'].lower()],
                          state_code=state['statecode'].lower())
        db.session.add(covid)
    covid = Covid(state='Daman and Diu', confirmed='0', 
                      active='0', recovered='0', 
                      deaths='0', deltaconfirmed='0', 
                      deltarecovered='0', deltadeaths='0',
                      state_code='dd')
    db.session.add(covid)
    db.session.commit()
    
    covid_india = Covid.query.filter_by(state='Total').first()
    timeseries_data = timeseries_data[-250:]
    for item in timeseries_data:
        timeseries = Timeseries(newcases=item['dailyconfirmed'], date=item['date'], covid=covid_india)
        db.session.add(timeseries)
    db.session.commit()
    
    data2 = data2[-750:]
    for state_code in states:
        covid_state = Covid.query.filter_by(state_code=state_code).first()
        for i in range(0, len(data2)):
            if i % 3 == 0:
                timeseries = Timeseries(newcases=data2[i][state_code], date=data2[i]["date"], covid=covid_state)
                db.session.add(timeseries)
    db.session.commit()

@main.route('/set_cookie', methods=['GET'])
def set_cookie():
    response = make_response(redirect(url_for('.index')))
    response.set_cookie('api_called', 'True')
    return response

@main.route('/get_data/<state_code>', methods=['GET'])
def get_data(state_code):
    timeseries_data = Covid.query.filter_by(state_code=state_code).first().timeseries
    values = [perday_data.newcases for perday_data in timeseries_data]
    labels = [perday_data.date for perday_data in timeseries_data]
    return jsonify({'payload':json.dumps({'values':values, 'labels':labels})})
    
@main.route('/', methods=['GET', 'POST'])
def index():
    if not request.cookies.get('api_called'):
        db.session.query(Covid).delete()
        db.session.query(Timeseries).delete()
        db.session.commit()
        fetch_api()
        return redirect(url_for('.set_cookie'))       
    form = SelectForm()
    daily_data = Covid.query.all()
    data_total = daily_data[0]    
    if not current_user.is_authenticated:
        return render_template('anonymous_user_index.html', data_total = data_total)
    else:
        selectValue = None
        if request.json != None:
            selectValue = request.json['state_code']            
        if selectValue == None:
            timeseries_data = Covid.query.filter_by(state_code='tt').first().timeseries
            values = [perday_data.newcases for perday_data in timeseries_data]
            labels = [perday_data.date for perday_data in timeseries_data]
        else:
            return redirect(url_for('main.get_data', state_code=selectValue))
    return render_template('index.html', data_total = data_total, data=daily_data, values=values, labels=labels, form=form)
    
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
