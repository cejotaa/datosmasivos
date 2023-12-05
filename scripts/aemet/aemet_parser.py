import json
import requests


class AEMETParser:

    def mun_parse(self, response):
        '''
        Parser de datos metereológicos de municipios
        :param response: respuesta de la petición
        '''

        tu_json = None
        if response.status_code == 200:
            data = response.json()
            tu_json = data

        dias = tu_json[0]["prediccion"]["dia"]
        datos = []

        for dia in dias:
            fecha = dia["fecha"]
            periodo = 0

            precipitacion = dia["probPrecipitacion"][periodo]["value"] if "probPrecipitacion" in dia else None
            viento = dia["viento"][periodo]["velocidad"]
            temp_max = dia["temperatura"]["maxima"] if "maxima" in dia["temperatura"] else None
            temp_min = dia["temperatura"]["minima"] if "minima" in dia["temperatura"] else None
            uv_max = dia["uvMax"] if "uvMax" in dia else None
            imagen_cielo = dia["estadoCielo"][periodo]["value"] if "estadoCielo" in dia else None
            estado_cielo = dia["estadoCielo"][periodo]["descripcion"] if "estadoCielo" in dia else None

            datos.append({
                "Fecha": fecha,
                "Periodo": periodo,
                "Temperatura máx": temp_max,
                "Temperatura mínima": temp_min,
                "Precipitación": precipitacion,
                "Viento": viento,
                "UvMax": uv_max,
                "estadoCielo": estado_cielo,
                "imagenCielo": imagen_cielo
            })
        return datos
