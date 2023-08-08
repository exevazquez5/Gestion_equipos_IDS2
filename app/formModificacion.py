from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class FormModificacion(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    tipo = StringField("Tipo", validators=[DataRequired()])
    marca = StringField("Marca", validators=[DataRequired()])
    modelo = StringField("Modelo", validators=[DataRequired()])
    desc = StringField("Desc", validators=[DataRequired()])
    submit = SubmitField("Modificar")