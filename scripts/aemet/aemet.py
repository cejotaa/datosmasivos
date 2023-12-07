import requests
import pandas as pd
import json
import os

from scripts.aemet.aemet_crawler import AEMETCrawler
from scripts.aemet.aemet_parser import AEMETParser


class AEMETApi:
    def __init__(self, api_key,codmun):
        self.api_key = api_key
        self.root_url = "https://opendata.aemet.es/opendata/api"

        crawler = AEMETCrawler()
        response = crawler.get_meteorological_data(self.root_url, self.api_key,codmun)

        parser = AEMETParser()
        parsed_data = parser.mun_parse(response)

        df = pd.DataFrame(parsed_data)

        # Save the data
        # Target folder
        carpeta_destino = 'datos/aemet'

        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)
        df.to_csv("datos/aemet/resp.csv")

        image_downloader = AEMETImageDownloader()
        image_downloader.download_images(df)


class AEMETImageDownloader:
    @staticmethod
    def download_images(df):
        carpeta_destino = 'datos/aemet/imagenes'

        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)

        for index, row in df.iterrows():
            imagen_cielo_png = row["imagenCielo"]
            url = f'https://www.aemet.es/imagenes/png/estado_cielo/{imagen_cielo_png}_g.png'

            if pd.notna(url):
                try:
                    respuesta = requests.get(url, stream=True)
                    respuesta.raise_for_status()

                    nombre_archivo = f"{index + 1}.jpg"
                    ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)

                    with open(ruta_archivo, 'wb') as archivo:
                        for chunk in respuesta.iter_content(chunk_size=8192):
                            archivo.write(chunk)
                    print(f"Imagen {index + 1} descargada con éxito.")
                except Exception as e:
                    print(f"Error al descargar la imagen {index + 1}: {str(e)}")
            else:
                print(f"No hay URL en la fila {index + 1}.")
