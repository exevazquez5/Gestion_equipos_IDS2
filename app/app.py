from sqlite3 import IntegrityError
from logging import exception

from flask_bootstrap import Bootstrap
from flask import Flask, render_template, redirect, url_for, flash, redirect,jsonify, request
from flask import abort
from flask import session
from flask import sessions
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from werkzeug.security import *

from formLogin import FormLogin
from formRegistro import FormRegistro
from formBusqueda import FormBusqueda
from formModificacion import FormModificacion


# Creamos una instancia de Flask (inicializa la app)
app = Flask(__name__) 
bootstrap = Bootstrap(app)

# Configs
import os
file_path = os.path.abspath(os.getcwd())+"\gestion_equipos.db" # cree una variable que guarda el path porque poniendola sola no funcionaba (solucion stackoverflow)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path # la concateno a la ruta de la URI de sqlalchemy
app.config['SECRET_KEY'] = 'asd'

db = SQLAlchemy(app) 

login_manager = LoginManager() 
login_manager.init_app(app)

migrate = Migrate(app, db)


# MODELS

class Equipo(db.Model):
    __tablename__ = "equipos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    marca = db.Column(db.String(20), nullable=False)
    modelo = db.Column(db.String(20), nullable=False)
    desc = db.Column(db.String(200), nullable=False)

    def __init__(self, nombre, tipo, marca, modelo, desc):
        super().__init__()
        self.nombre = nombre
        self.tipo = tipo
        self.marca = marca
        self.modelo = modelo
        self.desc = desc


    def __str__(self):
        return "\nNombre: {}, Tipo: {}, Marca: {}, Modelo: {}, Desc: {}.\n".format(
            self.nombre,
            self.tipo,
            self.marca,
            self.modelo,
            self.desc
        )


    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "marca": self.marca,
            "modelo": self.modelo,
            "desc": self.desc
        }
    
class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("Password no es un atributo de lectura")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)



# RUTAS

# rutas para login, register y logout
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/logout')
@login_required # Sólo usuarios autenticados pueden acceder a esta ruta
def logout(): 
    logout_user() # de Flask-Login. Elimina la sesión y cualquier información asociada al usuario actual
    flash('Se ha cerrado la sesión.')
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def register():
    form = FormRegistro()

    if request.method == "POST":
        if form.validate_on_submit():
            user = Usuario(email=form.email.data,
            username=form.username.data,
            password=form.password.data)
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash('Ya existe un Usuario con esas credenciales')
                return render_template('registro.html', form=form)
            flash('Ya podés ingresar al sistema.')
            return redirect(url_for('login'))

    return render_template('registro.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Verificar si el usuario ya está autenticado
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for('home'))

    form = FormLogin()

    if request.method == "POST":
        if form.validate_on_submit():
            user = Usuario.query.filter_by(username=form.username.data).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data) # de Flask-Login. Establece la sesión del usuario para rastrear y gestionar la identidad del mismo.
                return redirect(url_for('home'))
        flash('Error al iniciar sesión')

    return render_template('login.html', form=form)

#######################

#RUTA RENDERIZAR INDEX
@app.route('/')
def home():
    return render_template('index.html')

#RUTA RENDERIZAR FORMULARIO REGISTRO EQUIPO
@app.route('/registrar_equipo')
def registrar_equipo_render():
    return render_template("registrar_equipo.html")

#RUTA RENDERIZAR FORMULARIO BUSCAR EQUIPO por id
@app.route('/filtrar_equipo', methods=['GET'])
def filtrar_equipo_render():
    return render_template('filtrar_equipo.html')

#RUTA PARA LISTAR TODOS LOS EQUIPOS
@app.route('/equipos')
def listar_equipos_render():
    try:
        equipos = Equipo.query.all() #SELECT * FROM Equipos
        return render_template('equipos.html', lista_equipos=equipos)
    
    except Exception:
        exception("[SERVER]: Error -->")
        return jsonify({"msg": "Ha ocurrido un error"}), 500


#RUTA PARA BUSCAR UN EQUIPO POR ID
@app.route('/api/get_equipo/<id>', methods = ['GET'])
def get_equipo(id):
    equipo_buscado = Equipo.query.get(id)

    if equipo_buscado:
        return render_template("equipo.html", equipo_buscado=equipo_buscado)
    else:
        session['error_message'] = "No se encontró un equipo con ese número de orden."
        return redirect(url_for('buscar_equipo'))

#RUTA RENDERIZAR FORM BUSQUEDA
@app.route('/busqueda', methods=['GET', 'POST'])
def buscar_equipo():
    busqueda = FormBusqueda()

    if 'error_message' in session:
        flash(session['error_message'])
        session.pop('error_message')  # Limpiamos el mensaje de error de la sesión

    if request.method == 'POST':
        if busqueda.orden.data:
            return redirect(url_for('get_equipo', id=busqueda.orden.data))
        else:
            flash("Se debe ingresar un n° orden")
    return render_template("busqueda.html", form=busqueda)


#RUTA PARA REGISTRAR UN NUEVO EQUIPO
@app.route('/api/registrar_equipo', methods=['GET', 'POST'])
def registrar_equipo():
    if request.method == 'POST':
        try:
            nombre = request.form["nombre"]
            tipo = request.form["tipo"]
            marca = request.form["marca"]
            modelo = request.form["modelo"]
            desc = request.form["desc"]

            equipo = Equipo(nombre, tipo, marca, modelo, desc)
            db.session.add(equipo)
            db.session.commit()

            
            flash('Registro exitoso')
            return redirect(url_for('registrar_equipo_render'))
        
        except Exception:
            exception("\n[SERVER]: Error en la ruta /api/registrar_equipo. Log: \n")
            return redirect(url_for('registrar_equipo_render'))



#RUTA PARA FILTRAR EQUIPOS POR CUALQUIER PARAMETRO EN URL
@app.route('/api/filtrar_equipo_url', methods = ['GET'])
def filtrar_equipo():
    try:
        fields= {}
        if "nombre" in request.args:
            fields["nombre"] = request.args["nombre"]
        if "tipo" in request.args:
            fields["tipo"] = request.args["tipo"]
        if "marca" in request.args:
            fields["marca"] = request.args["marca"]
        if "modelo" in request.args:
            fields["modelo"] = request.args["modelo"]

        equipo = Equipo.query.filter_by(**fields).first()

        if not equipo:
            return jsonify({"msg": "Este cliente no tiene equipos en el taller"}), 200
        else:
            return jsonify(equipo.serialize()), 200

    except:
        exception("[SERVER]: Error -->")
        return jsonify({"msg": "Ha ocurrido un error"}), 500


#RUTA PARA BUSCAR UN EQUIPO POR FORMULARIO
@app.route('/api/filtrar_equipo/', methods = ['POST'])
def get_equipo_form():
    try:
        nombreCliente = request.form["nombre"]
        
        equipo = Equipo.query.filter(Equipo.nombre.like(f"%{nombreCliente}%")).first()
        if not equipo:
            return jsonify({"msg": "Este cliente no tiene equipos en el taller"}), 200
        else:
            return jsonify(equipo.serialize()), 200

    except:
        exception("[SERVER]: Error -->")
        return jsonify({"msg": "Ha ocurrido un error"}), 500
    

#RUTA EDITAR EQUIPO POR ID
@app.route('/api/editar_equipo/<int:id>', methods=['GET', 'POST'])
def editar_equipo(id):
    editar = FormModificacion()

    equipo_editar = Equipo.query.get_or_404(id)

    if request.method == 'POST':
        if editar.validate_on_submit():

            equipo_editar.nombre = editar.nombre.data
            equipo_editar.tipo = editar.tipo.data
            equipo_editar.marca = editar.marca.data
            equipo_editar.modelo = editar.modelo.data
            equipo_editar.desc = editar.desc.data
    
            db.session.add(equipo_editar)
            try:
                db.session.flush()
                db.session.commit()
                flash(f"Equipo {equipo_editar.id} modificado exitosamente.")
            except Exception as e:
                db.session.rollback()
                flash(f"Error al modificar el equipo: {str(e)}")
                return redirect(url_for('get_equipo', id=equipo_editar.id))
            
        else:
            flash("Los datos enviados no son válidos. Revisar el formulario.")
    
    editar.nombre.data = equipo_editar.nombre
    editar.tipo.data = equipo_editar.tipo
    editar.marca.data = equipo_editar.marca
    editar.modelo.data = equipo_editar.modelo
    editar.desc.data = equipo_editar.desc

    return render_template("modificar.html", form=editar, equipo_editar=equipo_editar)
    

#RUTA BORRAR EQUIPO POR ID
@app.route('/api/borrar_equipo/<int:id>', methods=['DELETE', 'POST'])
def borrar_equipo(id):
    if request.method == 'DELETE' or (request.method == 'POST' and request.form.get('_method') == 'DELETE'):
        equipo = Equipo.query.get(id)
        if equipo:
            db.session.delete(equipo)
            db.session.commit()
            return jsonify({'message': f'Equipo {id} eliminado exitosamente'}), 200
        else:
            return jsonify({'error': 'No se encontró el equipo'}), 404
    else:
        return jsonify({'error': 'Método no permitido'}), 405


# Manejo del error para métodos no permitidos
@app.errorhandler(405)
def metodo_no_permitido(error):
    flash('Método no permitido')
    return jsonify({"message": "Ha ocurrido un error"}), 405

if __name__ == '__main__':
    app.run(port=4000, debug=True)
    
