import requests
import json


class AEMETCrawler:

    def get_avisos_area(self, root_url, api_key, area='61'):
        '''
        Últimos avisos de fenómenos meteorológicos adversos elaborado para el área

        :param root_url:
        :param api_key:
        :param area:
        :return:
        '''
        url = f"{root_url}/avisos_cap/ultimoelaborado/area/{area}"
        querystring = {"api_key": api_key}
        headers = {'cache-control': "no-cache"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        datos_diccionario = json.loads(response.text)
        url_datos_meteo = datos_diccionario['datos']
        response = requests.get(url_datos_meteo)
        return response

    def get_meteorological_data(self, root_url, api_key, codigo_municipio='33002'):
        '''
        
        :param root_url:
        :param api_key:
        :param codigo_municipio:
        :return:
        '''
        url = f"{root_url}/prediccion/especifica/municipio/diaria/{codigo_municipio}"
        querystring = {"api_key": api_key}
        headers = {'cache-control': "no-cache"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        datos_diccionario = json.loads(response.text)
        url_datos_meteo = datos_diccionario['datos']
        response = requests.get(url_datos_meteo)
        return response

    def get_maestro_mun(self, root_url, api_key):
        '''

        :param root_url: root of aemet/api
        :param api_key: api key de aemet
        :return: lista que contiene todos los datos
        '''




        url = f"{root_url}/maestro/municipios/"
        querystring = {"api_key": api_key}
        headers = {'cache-control': "no-cache"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        datos_diccionario = json.loads(response.text)
        return datos_diccionario
