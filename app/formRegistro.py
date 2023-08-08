from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Length, Regexp, EqualTo

class FormRegistro(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Length(1, 64)])
    username = StringField('Nombre de Usuario', validators=[
    DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
    'Usernames must have only letters, '
    'numbers, dots or underscores')])
    password = PasswordField('Contraseña', validators=[
    DataRequired(), EqualTo('password2', message='Las contraseñas deben coincidir.')])
    password2 = PasswordField('Confirmar contraseña', validators=[DataRequired()])
    submit = SubmitField('Registrar')