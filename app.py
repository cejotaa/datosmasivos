from flask import Flask, redirect, url_for, render_template, request
from flask_wtf import FlaskForm
# from flask_pymongo import PyMongo

from wtforms import StringField, validators, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired

app = Flask(__name__, template_folder='website/resources/templates/', static_folder='website/resources/static/')
app.secret_key = "secret_key_123"
# Define database to use (check later)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
# mongo = PyMongo(app)

num_people = []
capitales = [
    ("A Coruña", "g187507"),
    ("Albacete", "g187486"),
    ("Alicante", "g1064230"),
    ("Almería", "g187429"),
    ("Oviedo", "g187452"),
    ("Ávila", "g311310"),
    ("Badajoz", "g262058"),
    ("Palma de Mallorca", "g187463"),
    ("Barcelona", "g187497"),
    ("Burgos", "g187491"),
    ("Cáceres", "g227852"),
    ("Cádiz", "g187432"),
    ("Santander", "g187484"),
    ("Castellón", "g187522"),
    ("Ciudad Real", "g187487"),
    ("Córdoba", "g187430"),
    ("Cuenca", "g262065"),
    ("Girona", "g187499"),
    ("Granada", "g187441"),
    ("Guadalajara", "g262063"),
    ("San Sebastián", "g187457"),
    ("Huelva", "g187442"),
    ("Huesca", "g187446"),
    ("Jaén", "g315916"),
    ("Logroño", "g187513"),
    ("Las Palmas", "g187472"),
    ("León", "g187492"),
    ("Lleida", "g187500"),
    ("Lugo", "g609027"),
    ("Madrid", "g187514"),
    ("Málaga", "g187438"),
    ("Murcia", "g187518"),
    ("Pamplona", "g187520"),
    ("Ourense", "g644337"),
    ("Palencia", "g652127"),
    ("Pontevedra", "g488307"),
    ("Salamanca", "g187493"),
    ("Santa Cruz de Tenerife", "g_50670"),
    ("Segovia", "g187494"),
    ("Sevilla", "g187443"),
    ("Soria", "g488305"),
    ("Tarragona", "g187503"),
    ("Teruel", "g580279"),
    ("Toledo", "g187489"),
    ("Valencia", "g187529"),
    ("Valladolid", "g187495"),
    ("Vitoria", "g187458"),
    ("Zamora", "g262064"),
]

'''
Auxiliar classes and functions for the forms
'''


class TravelForm(FlaskForm):
    destination = SelectField(label='Destino:', validators=[DataRequired()])
    people = SelectField(label='Número de personas:', choices=[], validators=[DataRequired()])
    days = SelectField(label='Número de días', choices=[], validators=[DataRequired()])
    way_transport = SelectField(label='Transporte', choices=[], validators=[DataRequired()])
    type_trip = SelectField(label='Tipo de viaje', validators=[DataRequired()])
    submit = SubmitField("Generar")


def populate(travel_form):
    # populating the options of number of people
    travel_form.people.choices = [(str(i), str(i)) for i in range(1, 20)]
    # populating the options of number of days
    travel_form.days.choices = [(str(i), str(i)) for i in range(1, 11)]
    # populating the ways of transport
    travel_form.way_transport.choices = [("car", "En coche"), ("foot", "Senderismo"), ("public", "Transporte público")]
    # populating the type of trip
    travel_form.type_trip.choices = [("cultural", "Cultural"), ("sporty", "Deporte")]

    # populating the destination dropdown
    travel_form.destination.choices = []

    for capital in capitales:
        travel_form.destination.choices.append(capital[0])


'''
Routing of the web
'''
# Creating the main view (Form Contact with the Destination, People, Days, Way of Transport, Type of trip)
@app.route("/", methods=["GET", "POST"])
def home():
    travel_form = TravelForm()
    populate(travel_form)
    # Get the results from the travel_form and process them -> redirect to /travel_list with the resulting data
    return render_template("travel_form.html", form=travel_form)

@app.route("/travel_list", methods=["GET", "POST"])
def travel_list():
    travel_form = TravelForm()

    return render_template("travel_form.html", form=travel_form)

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


if __name__ == '__main__':
    app.run(debug=True)
