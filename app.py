from flask import Flask, redirect, url_for, render_template, session, request
from flask_wtf import FlaskForm
from flask_pymongo import PyMongo
import random

from wtforms import StringField, validators, PasswordField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired
from scripts.GMaps import *
from scripts.scrapper_tripadvisor import *
from scripts.aemet.aemet import *
import csv

'''
    Configuring the app
'''
app = Flask(__name__, template_folder='website/resources/templates/', static_folder='website/resources/static/')
app.secret_key = "secret_key_123"
api_key_aemet = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMDA1MDc5NzBAYWx1bW5vcy51YzNtLmVzIiwianRpIjoiNjc4MWViYmItZjY0OC00MGIzLWJjMDctN2FiOTcyYWRiNGFhIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE2OTk2MzUyNjUsInVzZXJJZCI6IjY3ODFlYmJiLWY2NDgtNDBiMy1iYzA3LTdhYjk3MmFkYjRhYSIsInJvbGUiOiIifQ.yp7Maa4-Rshvm9CKIKjxDSLEZcpSCT6JrazmCPqrmX0"

# Define database to use (check later)
app.config["MONGO_URI"] = "mongodb://localhost:27017/routeMaster"
app.config["FLASK_DEBUG"] = True
mongo = PyMongo(app)
aux_list = []

'''
    Auxiliar arrays etc
'''
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
               9: 'Bilbao',  # 48 020
               10: 'Burgos',  # 09 059
               11: 'Caceres',  # 10 037
               12: 'Cadiz',  # 11 012
               13: 'Santander',  # 39 075
               14: 'Castellon de la Plana',  # 12 040
               15: 'Ciudad Real',  # 13 034
               16: 'Cordoba',  # 14 021
               17: 'Cuenca',  # 16 078
               18: 'Girona',  # 17 079
               19: 'Granada',  # 18 087
               20: 'Guadalajara',  # 19 190
               21: 'San Sebastián',  # 20 069
               22: 'Huelva',  # 21 041
               23: 'Huesca',  # 22 125
               24: 'Jaen',  # 23 050
               25: 'Logrono',  # 26 089
               26: 'Las Palmas de Gran Canaria',  # 35 016
               27: 'Leon',  # 24 089
               28: 'Lerida',  # 25 120
               29: 'Lugo',  # 27 028
               30: 'Madrid',  # 28 079
               31: 'Malaga',  # 29 067
               32: 'Murcia',  # 30 030
               33: 'Pamplona',  # 31 201
               34: 'Ourense',  # 32 054
               35: 'Palencia',  # 34 120
               36: 'Pontevedra',  # 36 038
               37: 'Salamanca',  # 37 274
               38: 'Santa Cruz de Tenerife',  # 38 038
               39: 'Segovia',  # 40 194
               40: 'Sevilla',  # 41 091
               41: 'Soria',  # 42 173
               42: 'Tarragona',  # 43 148
               43: 'Teruel',  # 44 216
               44: 'Toledo',  # 45 168
               45: 'Valencia',  # 46 250
               46: 'Valladolid',  # 47 186
               47: 'Vitoria Gasteiz',  # 01 059
               48: 'Zamora',  # 49 275
               49: 'Zaragoza'  # 50 297
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
    Auxiliar classes and functions for the travel form
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
        # TODO check the days and pass this value to the consultas(destination, tipo_viaje, days) to limit activities per days
        people = travel_form.people.data
        days = travel_form.days.data
        tipo_viaje = travel_form.type_trip.data
        destination = travel_form.destination.data
        session['startdate'] = travel_form.startdate.data
        session['tipo_viaje'] = tipo_viaje

        alojamiento, rutas = consultas(destination, tipo_viaje,days)
        for r in rutas: print(r)
        # Call the apis etc, get the data and process it, save it into a list
        session['alojamientos'] = alojamiento
        session['rutas'] = rutas
        return redirect(url_for('travel_list'))
    return render_template("travel_form.html", form=travel_form)


'''
    Communication with the apis
'''


def consultas(destino, tipo_viaje,dias):
    '''
        Auxiliar method that communicates with the apis, etc to extract data
    :param destino: string that shows the index in the list of cities
    :param tipo_viaje: string that can be "cultural", "sporty" or "mix"
    :param dias: number of days of the trip
    :return: the list of hotels, the complete set of routes per day
    '''
    rutas_completas = []
    # choices=[("cultural", "Cultural"), ("sporty", "Deporte"), ("mix", "Mixto")],


    alojamiento = busqueda(lista_ciudades[int(destino)]["Ciudad"])[0:2]  # solo queremos 2 alojamientos
    lista_tiempo = aemetapi(lista_ciudades[int(destino)]["CPRO"] + lista_ciudades[int(destino)]["CMUN"])

    if tipo_viaje == "cultural":
        # Change here 5 -> number of days
        actividades = tripadvisor(lista_ciudades[int(destino)]["TripAdvisor"])[0:int(dias)]
        print("Actividades:")
        print(len(actividades))
        rutas_completas.extend(aux_parse_activities(actividades, destino, lista_tiempo))
    elif tipo_viaje == "sporty":
        #    TODO check
        print("sporty")
        routes = mongoquery(mongo.db.route.find({'zona': lista_ciudades[int(destino)]["AllTrails"]}))[0:int(dias)]
        rutas_completas.extend(aux_parse_routes(routes, destino, lista_tiempo))
        # Change here 5 -> number of days

    else:
        if (random.randint(0, 1) == 0):
            # Change here 5 -> number of days
            actividades = tripadvisor(lista_ciudades[int(destino)]["TripAdvisor"])[0:int(int(dias)/2)]
            rutas_completas.extend(aux_parse_activities(actividades, destino, lista_tiempo))
            print("Tamaño actividades:")
            print(len(actividades))
            routes = mongoquery(mongo.db.route.find({'zona': lista_ciudades[int(destino)]["AllTrails"]}))[0:int(int(dias) - len(actividades))]
            rutas_completas.extend(aux_parse_routes(routes, destino, lista_tiempo))
        else : 
            routes = mongoquery(mongo.db.route.find({'zona': lista_ciudades[int(destino)]["AllTrails"]}))[0:int(int(dias)/2)]
            rutas_completas.extend(aux_parse_routes(routes, destino, lista_tiempo))
            actividades = tripadvisor(lista_ciudades[int(destino)]["TripAdvisor"])[0:int(int(dias) - len(routes))]
            rutas_completas.extend(aux_parse_activities(actividades, destino, lista_tiempo))
            
    return alojamiento, rutas_completas


'''
    Doing: Creating List of Route elements that have the complete set of interestint data
    ROUTE FORMAT
    
    Nombre: -> route.titulo | actividad.nombre
    Tipo: -> cultural (actividades) vs deportivo (routes
    Ubicación: -> destination
    Temperaturas: -> lista_tiempo[0].tmax lista_tiempo[0].tmin
    Ver más: -> resumen del resto de campos interesantes
'''


def aux_parse_activities(actividades, destino, lista_tiempo):
    '''
        Aux method to parse the data in a common format of route to show in the html
    :param actividades: list of activities to do
    :param destino: string del index de la lista de ciudades del destino
    :param lista_tiempo: list of seven days of temperature
    :return: list of parsed activities into the routes format
    '''
    rutas_completas = []
    destino = lista_ciudades[int(destino)]['Ciudad']
    temperatura = f"{lista_tiempo[0]['TMax']} / {lista_tiempo[0]['TMin']}"

    resumen = '\n'

    for i, temp_data in enumerate(lista_tiempo, start=1):
        resumen += (
            f'Día {i}: Fecha {escapeHTML(temp_data["Fecha"])}, '
            f'TMax: {escapeHTML(temp_data["TMax"])}, '
            f'TMin: {escapeHTML(temp_data["TMin"])}, '
            f'Precipitaciones: {escapeHTML(temp_data["Precipitacion"])}, '
            f'Viento: {escapeHTML(temp_data["Viento"])}, '
            f'Estado del cielo: {escapeHTML(temp_data["Estado_cielo"])}\n'
        )

    for actividad in actividades:
        elemento = {
            "id": actividad['Id'] if actividad['Id'] is not None else a,
            "nombre": actividad['Nombre'],
            "tipo": "Cultural",
            "ubicacion": destino,
            "temperatura": temperatura,
            "valoracion": f"'{actividad['Valoracion']}'",
            "tipoActividad": f"{actividad['Tipo'][0]}",
            "otros": resumen
        }
        rutas_completas.append(elemento)
        aux_list.append(elemento)

    return rutas_completas


def aux_parse_routes(routes, destino, lista_tiempo):

    rutas_completas = []
    destino = lista_ciudades[int(destino)]['Ciudad']
    temperatura = f"{lista_tiempo[0]['TMax']} / {lista_tiempo[0]['TMin']}"

    resumen = '\n'

    for i, temp_data in enumerate(lista_tiempo, start=1):
        resumen += (
            f'Día {i}: Fecha {escapeHTML(temp_data["Fecha"])}, '
            f'TMax: {escapeHTML(temp_data["TMax"])}, '
            f'TMin: {escapeHTML(temp_data["TMin"])}, '
            f'Precipitaciones: {escapeHTML(temp_data["Precipitacion"])}, '
            f'Viento: {escapeHTML(temp_data["Viento"])}, '
            f'Estado del cielo: {escapeHTML(temp_data["Estado_cielo"])}\n'
        )

    for route in routes:        
        elemento = {
            "id": route['id'],
            "nombre": route['titulo'],
            "tipo": route['type'],
            "ubicacion": route['location'],
            "temperatura": temperatura,
            "valoracion": f"'{route['rate']}'",
            "tipoActividad": f"{route['tags'][0]}",
            "otros": route['distancia']
        }
        rutas_completas.append(elemento)
        aux_list.append(elemento)
    return rutas_completas


def escapeHTML(text):
    # Reemplaza caracteres especiales con entidades HTML
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(html_escape_table.get(c, c) for c in text)


@app.route("/travel_list", methods=["GET", "POST"])
def travel_list():
    alojamientos = session.get('alojamientos')
    rutas = session.get('rutas')
    return render_template('travel_list.html', alojamientos=alojamientos, rutas=rutas)

@app.route('/travel_details/<int:ruta_id>', methods=["GET", "POST"])
def travel_details(ruta_id):
    # Lógica para obtener detalles de la ruta con ID 'ruta_id
    ruta = busca_id(ruta_id)
    # Renderiza una plantilla con los detalles o realiza otras acciones según sea necesario
    return render_template('travel_details.html', ruta=ruta)

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
                         'tags': result['tags'],
                         'type': 'Deporte'
                         }
        id += 1
        res.append(payload_route)
    return res


def busca_id(id):
    for i in aux_list:
        print(i)
        if i['id'] == id:
            return i


if __name__ == '__main__':
    app.run(debug=True)
