from time import sleep
import googlemaps

claveAPI = "AIzaSyAV50jKxT5jnmiIYR-EOCwtUZwkzsIxHwA"

# Rutas de montaña: park, natural_feature
# Comida: restaurant
# tourist_attraction
# campground => campings | rv_park => camping de caravanas

# Tipos eliminados: 'ammusement_park', 'aquarium', 'zoo'

# Emplear solo estos tipos
gastro_ruta = ['bar','restaurant']  # food
ruta_campo = ['campground','park','rv_park'] # natural_feature
cultural = ['tourist_attraction', 'city_hall']
alojamiento = ['lodging','campground','rv_park']
tipos_busqueda = ['point_of_interest']

def geolocalizacion(sitio):
    return googlemaps.Client(key=claveAPI).geocode(sitio)[0]['geometry']['location']

def incluye(lista1: list, elemento: dict):
    tipo = "hotel"
    if 'campground' in elemento['types']:
        tipo = "camping"
    elif 'rv_park' in elemento['types']:
        tipo="camping de caravanas"

    diccio = {
        "nombre": elemento["name"],
        "coordenadas": elemento["geometry"]["location"],
        "valoracion": elemento["rating"],
        "direccion": elemento["vicinity"],
        "tipo": tipo
    }
    lista1.append(diccio)

class GMaps():
    def __init__(self) -> None:
        self.map_client = googlemaps.Client(key=claveAPI)
        self.token = None
        self.loc = None
    
    def busqueda(self, ciudad):
        self.token = None
        self.loc = geolocalizacion(ciudad)

        response = self.map_client.places_nearby(
            location=self.loc,
            radius=5000,
            type=tipos_busqueda
        )

        mas = 'next_page_token' in response.keys()
        if mas:
            self.token = response['next_page_token']
        return (response['status'],response['results'],mas)
    
    def busqueda_alojamiento(self, ciudad, orden_distancia=False):
        self.token = None
        self.loc = geolocalizacion(ciudad)

        ranks = None
        if orden_distancia:
            ranks = "distance"

        # Los precios se ordenan de 0 a 4, siendo 0 las opciones más baratas y 4 las más caras
        response = self.map_client.places_nearby(
            location=self.loc,
            radius=5000,
            #type=tipos_busqueda,
            type=alojamiento,
            rank_by=ranks
        )

        mas = 'next_page_token' in response.keys()
        if mas:
            self.token = response['next_page_token']
        return (response['status'],response['results'],mas)
    
    def ampliar_busqueda(self):
        response = self.map_client.places_nearby(page_token=self.token)
        mas = 'next_page_token' in response.keys()
        if mas:
            self.token = response['next_page_token']
        return (response['status'],response['results'],mas)


# Si se copia esta funcion, modificar el valor de sleep, dependiendo del tiempo que se tarde entre peticiones
def busqueda(ciudad):
    mapas = GMaps()
    respuesta = mapas.busqueda_alojamiento(ciudad)
    
    res = []
    # res.extend(respuesta[1])
    for elem in respuesta[1]:
        incluye(res,elem)
    estado = respuesta[0]
    mas = respuesta[2]

    i = 1
    while i<3 and estado=="OK" and mas:
        # Hay que esperar un tiempo para que el servidor almacene el token de proxima pagina. Si no se le da tiempo, da error
        # Parece que con el filtrado que hacemos en local, este es el tiempo mínimo necesario para que se recupere sin error
        # Si surge algun error durante las pruebas, aumentar a 2 segundos. A partir de los 2 segundos no hay error
        sleep(1.9)
        respuesta = mapas.ampliar_busqueda()

        estado = respuesta[0]
        if estado=="OK":
            # res.extend(respuesta[1])
            for elem in respuesta[1]:
                incluye(res,elem)
            mas = respuesta[2]
        i += 1
    
    return res

if __name__=="__main__":
    # maps = GMaps()
    ciudad = input()
    # resp = maps.busqueda(ciudad)
    resp = busqueda(ciudad)
    # print(resp[0])
    # print(resp[1])
    pass