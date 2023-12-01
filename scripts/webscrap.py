import requests
from bs4 import BeautifulSoup
import time
import random
import json
import pymongo

random.seed(10)
espana = {
    'alava': 'vitoria-gasteiz',
    'albacete': 'albacete',
    'alicante': 'alicante',
    'almeria': 'almeria',
    'asturias': 'oviedo',
    'avila': 'avila',
    'badajoz': 'badajoz',
    'barcelona': 'barcelona',
    'burgos': 'burgos',
    'caceres': 'caceres',
    'cadiz': 'cadiz',
    'cantabria': 'santander',
    'castellon': 'castello-de-la-plana',
    'ciudad-real': 'ciudad-real',
    'cordoba': 'cordoba',
    'cuenca': 'cuenca',
    'girona': 'girona',
    'Granada': 'Granada',
    'guadalajara': 'guadalajara',
    'guipuzkoa': 'san-sebastián',
    'huelva': 'huelva',
    'huesca': 'huesca',
    'mallorca': 'palma',
    'jaen': 'jaen',
    'a-coruna': 'a-coruna',
    'la-rioja': 'logrono',
    'gran-canaria': 'las-palmas-de-gran-canaria',
    'leon': 'leon',
    'lleida': 'lerida',
    'lugo': 'lugo',
    'madrid': 'madrid',
    'malaga': 'malaga',
    'murcia': 'murcia',
    'navarre': 'pamplona',
    'ourense': 'ourense',
    'palencia': 'palencia',
    'pontevedra': 'pontevedra',
    'salamanca': 'salamanca',
    'tenerife': 'santa-cruz-de-tenerife',
    'segovia': 'segovia',
    'sevilla': 'sevilla',
    'soria': 'soria',
    'tarragona': 'tarragona',
    'teruel': 'teruel',
    'toledo': 'toledo',
    'valencia': 'valencia',
    'valladolid': 'valladolid',
    'biscay': 'bilbao',
    'zamora': 'zamora',
    'zaragoza': 'zaragoza'
}

json_list = []
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Accept-Language': 'es,es-ES;q=0.9,en;q=0.8'
            }


for a in espana:
    print("provincia: " + a + ", capital de provincia: " + espana[a])
    
    response = requests.get('https://www.alltrails.com' + '/es/spain/'+ a + '/' + espana[a] +'/' , headers=headers)
    
    
    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')
        data = soup.findAll('a', attrs={'class' : 'MAeU7STjXOwFXsjoI5meHg== E8W6wpmnshxeFElAofUjoA=='}, href=True)
        rutas = []

        for url in data:

            if '/es/ruta/spain/' in url['href'] and len(rutas) < 5 and url['href'] not in rutas:

                rutas.append(url['href'])
                response = requests.get('https://www.alltrails.com' + url['href'], headers=headers)
                
                if response.status_code == 200:

                    tags = []
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.find('h1', attrs={'class' : 'xlate-none TrailDetailsCard-module__name___fVfrR'}).get_text()
                    ubication = soup.find('a', attrs={'class' : 'xlate-none styles-module__location___hAqkh TrailDetailsCard-module__location___xmmiJ'}).get_text()
                    distance = soup.find('span', attrs={'class' : 'styles-module__detailData___fxmwv'}).get_text()
                    lista = soup.find_all('span', attrs={'class' : 'WjApmTpVDxquc+eB9ckN1g=='})
                    for l in lista:
                        tags.append(l.get_text())
                    rate = soup.find('div', attrs={'class' : '_8wnk+S3qa73g1dgF5H-ndw=='}).get_text()

                    payload_route = {'titulo' : title,
                                    'ubicacion' : ubication,
                                    'distancia': distance, 
                                    'tags': tags,
                                    'valoracion': rate,
                                    'url' : ('https://www.alltrails.com' + url['href']),
                                    'zona' : a + ', ' + espana[a] }
                    
                    print(payload_route)
                    json_list.append(payload_route)

                    sleep = 15 + random.random()
                    print(sleep)
                    time.sleep(sleep)
                else: 
                    print(f"Error al obtener la página: {response.status_code}")
                    print(f"La url es: {('https://www.alltrails.com' + url['href'])}")

    else:
        print(f"Error al obtener la página: {response.status_code}")

with open("routes.json", "w") as json_file:
    json.dump(json_list, json_file, indent=2)

with open("routes.json", "r") as json_file:
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    db = client["routeMaster"]

    collection = db["route"]

    file = json.load(json_file)

    result = collection.insert_many(file)

    print(f"Los datos han sido insertados en la base de datos con este id: {result.inserted_ids}")

    client.close()