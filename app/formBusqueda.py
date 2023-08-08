from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class FormBusqueda(FlaskForm):
    orden = IntegerField("Ingrese el N° Orden", validators=[DataRequired()])
    submit = SubmitField("Buscar")