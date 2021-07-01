from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import Role, User

class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
    

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
    
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user
        
    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
            
    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
      
class SelectForm(FlaskForm):

    state = SelectField('State', choices=[('None', 'India'), 
                                         ('an', 'Andaman and Nicobar Islands'),
                                         ('ap', 'Andhra Pradesh'),
                                         ('ar', 'Arunachal Pradesh'),
                                         ('as', 'Assam'),
                                         ('br', 'Bihar'),
                                         ('ch', 'Chandigarh'),
                                         ('ct', 'Chhattisgarh'),
                                         ('dd', 'Daman and Diu'),
                                         ('dl', 'Delhi'),
                                         ('dn', 'Dadra and Nagar Haveli'),
                                         ('ga', 'Goa'),
                                         ('gj', 'Gujarat'),
                                         ('hp', 'Himachal Pradesh'),
                                         ('hr', 'Haryana'),
                                         ('jh', 'Jammu and Kashmir'),
                                         ('jk', 'Jharkhand'),
                                         ('ka', 'Karnataka'),
                                         ('kl', 'Kerala'),
                                         ('la', 'Lakshadweep'),
                                         ('ld', 'Ladakh'),
                                         ('mh', 'Maharashtra'),
                                         ('ml', 'Meghalaya'),
                                         ('mn', 'Manipur'),
                                         ('mp', 'Madhya Pradesh'),
                                         ('mz', 'Mizoram'),
                                         ('nl', 'Nagaland'),
                                         ('or', 'Odisha'),
                                         ('pb', 'Punjab'),
                                         ('py', 'Puducherry'),
                                         ('rj', 'Rajasthan'),
                                         ('sk', 'Sikkim'),
                                         ('tg', 'Telangana'),
                                         ('tn', 'Tamil Nadu'),
                                         ('up', 'Uttar Pradesh'),
                                         ('ut', 'Uttarakhand'),
                                         ('wb', 'West Bengal')])    
            
