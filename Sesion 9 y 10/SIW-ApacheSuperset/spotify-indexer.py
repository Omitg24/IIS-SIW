import json # Para poder trabajar con objetos JSON

from elasticsearch import Elasticsearch
from elasticsearch import helpers

def main():
    from datetime import datetime

    inicio = datetime.now()

    # Password para el usuario 'elastic' generada por Elasticsearch
    #
    ELASTIC_PASSWORD = "dKPZ*UTCUQKn83cfR8vw" # qozzfT869o6OKIp1Y2nQ"

    # Creamos el cliente y lo conectamos a nuestro servidor
    #
    global es

    es = Elasticsearch(
        "https://localhost:9200",
        ca_certs="./http_ca.crt",
        basic_auth=("elastic", ELASTIC_PASSWORD)
    )

    # Creamos el índice
    #
    # Si no se crea explícitamente se crea al indexar el primer documento
    #
    # Debemos crearlo puesto que el mapeado por defecto (mapping) de algunos
    # campos, no es satisfactorio.
    #
    es.indices.create(index="spotify-songs", ignore=400)

    # Se especifican los tipos que no sirven por defecto...
    #
    argumentos={
      "properties": {
        "track_album_release_date": {
          "type":"date",
          "format": "yyyy-MM-dd"
        }
      }
    }
    es.indices.put_mapping(index="spotify-songs",body=argumentos)

    global contador
    contador = 0

    tamano = 10*1024*1024 # Para leer 10MB, tamaño estimado de manera experimental
    fh = open("files/spotify_songs.ndjson", 'rt', encoding="utf-8")
    lineas = fh.readlines(tamano)
    while lineas:
      procesarLineas(lineas)
      lineas = fh.readlines(tamano)
    fh.close()

    fin = datetime.now()

    print(fin-inicio)

# Aquí indexaremos los documentos en bloques
def procesarLineas(lineas):
  jsonvalue = []

  for linea in lineas:
    datos = json.loads(linea) # Para acceder al diccionario
    datos["_index"] = "spotify-songs"
    jsonvalue.append(datos)

  num_elementos = len(jsonvalue)
  try:
    resultado = helpers.bulk(es,jsonvalue,chunk_size=num_elementos,request_timeout=200)
  except Exception as e:
    print(e)

  # Habría que procesar el resultado para ver que todo vaya bien...

  global contador

  contador += num_elementos
  print(contador)

if __name__ == '__main__':
    main()