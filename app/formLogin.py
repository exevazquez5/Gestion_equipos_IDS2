from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
class FormLogin(FlaskForm):
    username = StringField("Nombre de usuario", validators=[DataRequired(), Length(1, 60)])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    remember_me = BooleanField("Mantener la sesión iniciada")
    submit = SubmitField("Ingresar")