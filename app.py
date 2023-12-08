from flask import Flask, redirect, url_for, render_template, session, request
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from flask_pymongo import PyMongo

from wtforms import StringField, validators, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired
from scripts.GMaps import *
from scripts.scrapper_tripadvisor import *
from scripts.aemet.aemet import *
import csv

app = Flask(__name__, template_folder='website/resources/templates/', static_folder='website/resources/static/')
app.secret_key = "secret_key_123"
api_key_aemet = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMDA1MDc5NzBAYWx1bW5vcy51YzNtLmVzIiwianRpIjoiNjc4MWViYmItZjY0OC00MGIzLWJjMDctN2FiOTcyYWRiNGFhIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE2OTk2MzUyNjUsInVzZXJJZCI6IjY3ODFlYmJiLWY2NDgtNDBiMy1iYzA3LTdhYjk3MmFkYjRhYSIsInJvbGUiOiIifQ.yp7Maa4-Rshvm9CKIKjxDSLEZcpSCT6JrazmCPqrmX0"

# Define database to use (check later)
app.config["MONGO_URI"] = "mongodb://localhost:27017/routeMaster"
mongo = PyMongo(app)

num_people = []
destination = {'': 'Seleccione su destino',
               0: 'A Coruna',  # 15 030
               1: 'Albacete',  # 02 003
               2: 'Alicante',  # 03 014
               3: 'Almeria',  # 04 013
               4: 'Oviedo',  # 33 044
               5: 'Avila',  # 08 011
               6: 'Badajoz',  # 06 015
               7: 'Palma de Mallorca',  # 07 040
               8: 'Barcelona',  # 08 019
               9: 'Burgos',  # 09 059
               10: 'Caceres',  # 10 037
               11: 'Cadiz',  # 11 012
               12: 'Santander',  # 39 075
               13: 'Castellon de la Plana',  # 12 040
               14: 'Ciudad Real',  # 13 034
               15: 'Cordoba',  # 14 021
               16: 'Cuenca',  # 16 078
               17: 'Girona',  # 17 079
               18: 'Granada',  # 18 087
               19: 'Guadalajara',  # 19 190
               20: 'San Sebastián',  # 20 069
               21: 'Huelva',  # 21 041
               22: 'Huesca',  # 22 125
               23: 'Jaen',  # 23 050
               24: 'Logrono',  # 26 089
               25: 'Las Palmas de Gran Canaria',  # 35 016
               26: 'Leon',  # 24 089
               27: 'Lerida',  # 25 120
               28: 'Lugo',  # 27 028
               29: 'Madrid',  # 28 079
               30: 'Malaga',  # 29 067
               31: 'Murcia',  # 30 030
               32: 'Pamplona',  # 31 201
               33: 'Ourense',  # 32 054
               34: 'Palencia',  # 34 120
               35: 'Pontevedra',  # 36 038
               36: 'Salamanca',  # 37 274
               37: 'Santa Cruz de Tenerife',  # 38 038
               38: 'Segovia',  # 40 194
               39: 'Sevilla',  # 41 091
               40: 'Soria',  # 42 173
               41: 'Tarragona',  # 43 148
               42: 'Teruel',  # 44 216
               43: 'Toledo',  # 45 168
               44: 'Valencia',  # 46 250
               45: 'Valladolid',  # 47 186
               46: 'Vitoria Gasteiz',  # 01 059
               47: 'Zamora',  # 49 275
               48: 'Zaragoza',  # 50 297
               'biscay': 'Bilbao'  # 48 020
               }

lista_ciudades = []

csv_path = 'ciudades.csv'
with open(csv_path, 'r', encoding="utf-8") as cities:
    csv_row = csv.reader(cities)
    for row in csv_row:
        payload = {
            "Ciudad": row[0],
            "TripAdvisor": row[1],
            "COADUTO": row[2],
            "CPRO": row[3],
            "CMUN": row[4],
            "DC": row[5],
            "AllTrails": row[7],
        }
        lista_ciudades.append(payload)
    del lista_ciudades[0]

'''
Auxiliar classes and functions for the forms
'''


class TravelForm(FlaskForm):
    # populating the destination dropdown
    choices_dest = [(str(i), str(destination[i])) for i in destination]

    startdate = DateField('Start Date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    destination = SelectField(label='Destino:', choices=choices_dest, validators=[DataRequired()])
    people = SelectField(label='Número de personas:', choices=[(str(i), str(i)) for i in range(1, 20)],
                         validators=[DataRequired()])
    days = SelectField(label='Número de días', choices=[(str(i), str(i)) for i in range(1, 6)],
                       validators=[DataRequired()])
    type_trip = SelectField(label='Tipo de viaje',
                            choices=[("cultural", "Cultural"), ("sporty", "Deporte"), ("mix", "Mixto")],
                            validators=[DataRequired()])
    submit = SubmitField("Generar")


'''
Routing of the web
'''


# Creating the main view (Form Contact with the Destination, People, Days, Way of Transport, Type of trip)
@app.route("/", methods=["GET", "POST"])
def form_route():
    travel_form = TravelForm()

    # Get the results from the travel_form and process them -> redirect to /travel_list with the resulting data
    if travel_form.validate_on_submit():
        people = travel_form.people.data
        days = travel_form.days.data
        tipo_viaje = travel_form.type_trip.data
        destination = travel_form.destination.data
        session['startdate'] = travel_form.startdate.data
        session['tipo_viaje'] = tipo_viaje

        alojamiento, rutas = consultas(destination, tipo_viaje)
        # Call the apis etc, get the data and process it, save it into a list
        session['alojamientos'] = alojamiento
        session['rutas']=rutas
        return redirect(url_for('travel_list'))
    return render_template("travel_form.html", form=travel_form)


def consultas(destino, tipo_viaje):
    aux = []
    routes = []
    rutas_completas = []
    rutas = []
    # choices=[("cultural", "Cultural"), ("sporty", "Deporte"), ("mix", "Mixto")],

    alojamiento = busqueda(lista_ciudades[int(destino)]["Ciudad"])[0:2]  # solo queremos 2 alojamientos
    lista_tiempo = aemetapi(lista_ciudades[int(destino)]["CPRO"] + lista_ciudades[int(destino)]["CMUN"])

    if tipo_viaje == "cultural":
        actividades = tripadvisor(lista_ciudades[int(destino)]["TripAdvisor"])[0:5]

        rutas_completas.extend(aux_parse_activities(actividades, destino, lista_tiempo))
    elif tipo_viaje == "sporty":
        #routes = mongoquery(mongo.db.route.find({'zona': lista_ciudades[int(destino)]["AllTrails"]}))[0:5]
        print("routes things and stuff")
    else:
        actividades = tripadvisor(lista_ciudades[int(destino)]["TripAdvisor"])[0:5]
        rutas_completas.extend(aux_parse_activities(actividades, destino, lista_tiempo))
        #routes = mongoquery(mongo.db.route.find({'zona': lista_ciudades[int(destino)]["AllTrails"]}))

    app.logger.info(lista_tiempo)
    return alojamiento, rutas_completas

# Doing: Creating List of Route elements that have the complete set of data of
    #  Nombre: -> route.titulo | actividad.nombre
    #  Tipo: -> cultural (actividades) vs deportivo (routes
    #  Ubicación: -> destination
    #  Temperaturas: -> lista_tiempo[0].tmax lista_tiempo[0].tmin
    #  Ver más: el resto de datos.

def aux_parse_activities(actividades, destino, lista_tiempo):
    rutas_completas = []
    destino = lista_ciudades[int(destino)]['Ciudad']
    temperatura = f"{lista_tiempo[0]['TMax']} / {lista_tiempo[0]['TMin']}"

    for actividad in actividades:

        elemento = {
            "nombre": actividad['Nombre'],
            "tipo": "Cultural",
            "ubicacion": destino,
            "temperatura": temperatura,
            "otros": "Detalles de la actividad"
        }
        rutas_completas.append(elemento)
    return rutas_completas

@app.route("/travel_list", methods=["GET", "POST"])
def travel_list():
    alojamientos = session.get('alojamientos')
    rutas = session.get('rutas')
    return render_template('travel_list.html', alojamientos=alojamientos, rutas=rutas)


# decorator for route(argument) function
@app.route('/admin')
# binding to hello_admin call
def hello_admin():
    return 'Hello Admin'


@app.route('/guest/<guest>')
# binding to hello_guest call
def hello_guest(guest):
    return 'Hello %s as Guest' % guest


@app.route('/user/<name>')
def hello_user(name):
    # dynamic binding of URL to function
    if name == 'admin':
        return redirect(url_for('hello_admin'))
    else:
        return redirect(url_for('hello_guest'
                                , guest=name))


def aemetapi(codmun):
    AEMETApi(api_key_aemet, codmun)
    csv_file_path = './datos/aemet/resp.csv'
    aemet = []
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            fila = {
                'id': row[0],
                'Fecha': row[1][:10],
                'TMax': row[3],
                'TMin': row[4],
                'Precipitacion': row[5],
                'Viento': row[6],
                'Estado_cielo': row[7],
                'Imagen_cielo': row[8]
            }
            aemet.append(fila)
    del aemet[0]

    app.logger.info(aemet)
    return aemet


def mongoquery(query):
    res = []
    id = 0
    for result in query:
        # app.logger.info(result['zona'])
        payload_route = {'id': id,
                         'location': result['ubicacion'],
                         'distancia': result['distancia'],
                         'titulo': result['titulo'],
                         'url': result['url'],
                         'rate': result['valoracion'],
                         'type': 'ruta'
                         }
        id += 1
        res.append(payload_route)
    return res


if __name__ == '__main__':
    app.run(debug=True)
