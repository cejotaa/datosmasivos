import requests
from bs4 import BeautifulSoup
import re

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
    ("Bilbao", "g187454"),
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
    ("Zaragoza", "g187448")
]


def obtener_codigo(capitales, argumento):
    for capital, codigo in capitales:
        if capital == argumento:
            return codigo
    return None


def procesar_actividades(actividades):
    for actividad in actividades:
        # Procesar el campo 'Nombre'
        nombre = actividad["Nombre"]
        # Dividir el nombre usando el patrón "número punto espacio"
        partes_nombre = nombre.split('. ')
        # Tomar la última parte del nombre (después del último número y punto)
        nuevo_nombre = partes_nombre[-1]
        # Actualizar el campo 'Nombre'
        actividad["Nombre"] = nuevo_nombre

        # Procesar el campo 'Tipo'
        tipo = actividad["Tipo"]
        # Dividir el tipo usando el separador " • "
        tipos = tipo.split(' • ')
        # Actualizar el campo 'Tipo' con la lista de tipos
        actividad["Tipo"] = tipos

        valoracion_original = actividad["Valoracion"]
        # Utilizar expresiones regulares para extraer el número de la valoración original
        match = re.search(r'\d+\.\d+', valoracion_original)
        if match:
            numero_valoracion = match.group()
            # Reemplazar el punto con coma para obtener el formato deseado
            nueva_valoracion = numero_valoracion.replace('.', ',')
            # Actualizar el campo 'Valoracion' con el nuevo formato
            actividad["Valoracion"] = nueva_valoracion


def process_name(nombre):
    # Procesar el campo 'Nombre'
    # Dividir el nombre usando el patrón "número punto espacio"
    partes_nombre = nombre.split('. ')
    # Tomar la última parte del nombre (después del último número y punto)
    nuevo_nombre = partes_nombre[-1]
    # Actualizar el campo 'Nombre'
    return nuevo_nombre


def process_tipo(tipo):
    # Procesar el campo 'Tipo'
    # Dividir el tipo usando el separador " • "
    tipos = tipo.split(' • ')
    # Actualizar el campo 'Tipo' con la lista de tipos
    return tipos

def process_valoracion(valoracion):
    # Utilizar expresiones regulares para extraer el número de la valoración original
    match = re.search(r'\d+\.\d+', valoracion)
    if match:
        numero_valoracion = match.group()
        # Reemplazar el punto con coma para obtener el formato deseado
        nueva_valoracion = numero_valoracion.replace('.', ',')
        # Actualizar el campo 'Valoracion' con el nuevo formato
        return nueva_valoracion
    return valoracion

def tripadvisor(argumento):
    error = False
    # argumento = input("Introduce el nombre de la ciudad: ")
    # codigo_ciudad = obtener_codigo(capitales,argumento)

    # URL de la página de resultados de TripAdvisor
    # https://www.tripadvisor.com/Attractions-g187452-Activities-oa0
    url = f"https://www.tripadvisor.com/Attractions-{argumento}-Activities-oa0"
    print(url)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML/like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36'
    }

    # Realizar una solicitud HTTP para obtener la página
    response = requests.get(url, headers=headers, timeout=30)
    # Parsear el contenido de la página con BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    activities_containers = soup.find_all("div", class_="hZuqH y")
    print("ACTIVITIES CONTAINER")
    print(len(activities_containers))

    i = 0
    actividades = []

    for container in activities_containers:
        error, name = name_extractor(container)
        error, tipo = tipe_activity_extractor(container)
        error, valoracion = valoration_extractor(container)

        actividad = {
            "Id": i,
            "Nombre": name,
            "Tipo": tipo,
            "Valoracion": valoracion,
            "Error": str(error)
        }

        actividades.append(actividad)
        i += 1
        if i >= 30:
            break

    return actividades

    # # Imprime el resultado esperado
    # for actividad in actividades:
    #     print("Nombre:", actividad["Nombre"])
    #     print("Tipo:", actividad["Tipo"])
    #     print("Valoracion:", actividad["Valoracion"])
    #     print()

    # df = pd.DataFrame(actividades)
    # df.to_json("actividades.json", orient="records")


def valoration_extractor(container):
    error = False
    try:
        valoracion = container.find('svg')['aria-label']
        valoracion = process_valoracion(valoracion)
        print("valoracion de la actividad: " + valoracion)
    except:
        print("Tipo de valoracion mal")
        valoracion = "No encontrado"
        error = True
    return error, valoracion


def tipe_activity_extractor(container):
    error = False
    try:
        tipo = container.find("div", class_="biGQs _P pZUbB hmDzD").text.strip()
        tipo = process_tipo(tipo)
        print("tipo de la actividad: " + tipo)
    except:
        print("Tipo de actividad mal")
        tipo = "No encontrado"
        error = True
    return error, tipo


def name_extractor(container):
    error = False
    try:
        name = container.find("div", class_="XfVdV o AIbhI").text.strip()
        name = process_name(name)
        print("Nombre de la actividad: " + name)
    except:
        print("Nombre mal")
        name = "No encontrado"
        error = True
    return error, name
